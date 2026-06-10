from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class MqttConfig:
    broker: str
    port: int = 1883
    client_id: str = ""


@dataclass
class SensorConfig:
    id: str
    type: str
    interface: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeConfig:
    node_id: str
    mqtt: MqttConfig
    sensors: list[SensorConfig]
    poll_interval: int = 30


def load_config(path: str = "config.yaml") -> NodeConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)

    for key in ("node_id", "mqtt", "sensors"):
        if key not in raw:
            raise ValueError(f"Missing required config key: '{key}'")

    mqtt_raw = raw["mqtt"]
    if not isinstance(mqtt_raw, dict) or not mqtt_raw.get("broker"):
        raise ValueError("mqtt.broker is required")
    mqtt_cfg = MqttConfig(
        broker=mqtt_raw["broker"],
        port=int(mqtt_raw.get("port", 1883)),
        client_id=mqtt_raw.get("client_id", ""),
    )

    sensors_raw = raw["sensors"]
    if not isinstance(sensors_raw, list) or len(sensors_raw) == 0:
        raise ValueError("sensors must be a non-empty list")

    seen_ids: set[str] = set()
    sensors: list[SensorConfig] = []
    for i, s in enumerate(sensors_raw):
        for key in ("id", "type", "interface"):
            if not s.get(key):
                raise ValueError(f"sensors[{i}]: missing required field '{key}'")
        sensor_id = s["id"]
        if sensor_id in seen_ids:
            raise ValueError(f"Duplicate sensor id: '{sensor_id}'")
        seen_ids.add(sensor_id)
        sensors.append(SensorConfig(
            id=sensor_id,
            type=s["type"],
            interface=s["interface"],
            params=s.get("params") or {},
        ))

    node_id = str(raw["node_id"])
    if not mqtt_cfg.client_id:
        mqtt_cfg.client_id = node_id

    return NodeConfig(
        node_id=node_id,
        mqtt=mqtt_cfg,
        sensors=sensors,
        poll_interval=int(raw.get("poll_interval", 30)),
    )
