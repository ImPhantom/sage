from __future__ import annotations

import asyncio
import logging
import socket
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from config import NodeConfig

log = logging.getLogger(__name__)

_INITIAL_DELAY = 2.0
_MAX_DELAY = 60.0
_NON_RETRYABLE_4XX = {400, 401, 403, 409, 410, 422}


def _get_lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        log.warning("Could not detect LAN IP — falling back to 127.0.0.1")
        return "127.0.0.1"


async def announce_cameras(config: NodeConfig) -> None:
    if not config.cameras:
        log.info("Camera announcement skipped: no cameras configured")
        return
    if not config.backend:
        log.info("Camera announcement skipped: no backend URL configured")
        return

    local_ip = _get_lan_ip()
    log.debug("Detected LAN IP: %s", local_ip)

    payload = [
        {"id": cam.id, "rtsp_url": f"rtsp://{local_ip}:8554/{cam.id}"}
        for cam in config.cameras
    ]
    url = f"{config.backend.url}/nodes/{config.node_id}/cameras"

    delay = _INITIAL_DELAY
    attempt = 0

    async with aiohttp.ClientSession() as session:
        while True:
            attempt += 1
            log.debug("Announcing %d camera(s) to %s (attempt %d)", len(payload), url, attempt)
            try:
                async with session.post(
                    url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status in (200, 201, 204):
                        log.info(
                            "Cameras announced successfully: %d camera(s) registered with backend",
                            len(payload),
                        )
                        return
                    if resp.status in _NON_RETRYABLE_4XX:
                        body = await resp.text()
                        log.error(
                            "Camera announcement aborted: server returned %d (non-retryable). "
                            "Response: %s",
                            resp.status,
                            body[:200],
                        )
                        return
                    log.warning(
                        "Camera announcement attempt %d failed (HTTP %d), retrying in %.0fs",
                        attempt,
                        resp.status,
                        delay,
                    )
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                log.warning(
                    "Camera announcement attempt %d failed (%s: %s), retrying in %.0fs",
                    attempt,
                    type(exc).__name__,
                    exc,
                    delay,
                )

            await asyncio.sleep(delay)
            delay = min(delay * 2, _MAX_DELAY)
