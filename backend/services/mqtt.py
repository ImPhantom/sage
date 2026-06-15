import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone

import paho.mqtt.client as paho
from fastapi import WebSocket

log = logging.getLogger(__name__)

connected_websockets: set[WebSocket] = set()

_client: paho.Client | None = None
_loop: asyncio.AbstractEventLoop | None = None


async def _broadcast(payload: str) -> None:
    dead: set[WebSocket] = set()
    for ws in connected_websockets:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    connected_websockets.difference_update(dead)


def _on_message(client, userdata, msg) -> None:
    parts = msg.topic.split("/")
    if len(parts) != 4 or parts[0] != "grows":
        return
    _, node_id, sensor_id, metric = parts

    raw = msg.payload.decode("utf-8", errors="replace")
    try:
        value = float(raw)
    except ValueError:
        value = raw

    payload = json.dumps({
        "node_id": node_id,
        "sensor_id": sensor_id,
        "metric": metric,
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    if _loop is not None:
        asyncio.run_coroutine_threadsafe(_broadcast(payload), _loop)


def start(loop: asyncio.AbstractEventLoop) -> None:
    global _client, _loop
    _loop = loop
    host = os.environ.get("MQTT_BROKER", "localhost")
    port = int(os.environ.get("MQTT_PORT", "1883"))
    log.info("Connecting to MQTT broker at %s:%s", host, port)

    _client = paho.Client()
    _client.on_message = _on_message

    for attempt in range(1, 11):
        try:
            _client.connect(host, port)
            break
        except OSError as exc:
            if attempt == 10:
                raise
            log.warning("MQTT connect attempt %d/10 failed (%s), retrying in 3s…", attempt, exc)
            time.sleep(3)

    _client.subscribe("grows/#")
    _client.loop_start()


def stop() -> None:
    if _client is not None:
        _client.loop_stop()
        _client.disconnect()
