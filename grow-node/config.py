from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

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
class CameraConfig:
    id: str
    type: str  # rpi_csi | usb | rtsp
    params: dict[str, Any] = field(default_factory=dict)


_CAMERA_TYPES = {"rpi_csi", "usb", "rtsp"}
_CAMERA_REQUIRED_PARAMS: dict[str, str] = {
    "usb": "device",
    "rtsp": "url",
}


@dataclass
class BackendConfig:
    url: str


@dataclass
class NodeConfig:
    node_id: str
    mqtt: MqttConfig
    sensors: list[SensorConfig]
    poll_interval: int = 30
    cameras: list[CameraConfig] = field(default_factory=list)
    backend: Optional[BackendConfig] = None


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

    cameras: list[CameraConfig] = []
    cameras_raw = raw.get("cameras") or []
    if cameras_raw:
        if not isinstance(cameras_raw, list):
            raise ValueError("cameras must be a list")
        seen_cam_ids: set[str] = set()
        for i, c in enumerate(cameras_raw):
            for key in ("id", "type"):
                if not c.get(key):
                    raise ValueError(f"cameras[{i}]: missing required field '{key}'")
            cam_id = c["id"]
            cam_type = c["type"]
            if cam_id in seen_cam_ids:
                raise ValueError(f"Duplicate camera id: '{cam_id}'")
            seen_cam_ids.add(cam_id)
            if cam_type not in _CAMERA_TYPES:
                raise ValueError(
                    f"cameras[{i}]: unknown type '{cam_type}' (must be one of: {', '.join(sorted(_CAMERA_TYPES))})"
                )
            params = c.get("params") or {}
            required_param = _CAMERA_REQUIRED_PARAMS.get(cam_type)
            if required_param and required_param not in params:
                raise ValueError(
                    f"cameras[{i}] (type={cam_type!r}): params.{required_param} is required"
                )
            cameras.append(CameraConfig(id=cam_id, type=cam_type, params=params))

    backend_cfg: Optional[BackendConfig] = None
    backend_raw = raw.get("backend")
    if backend_raw:
        if not isinstance(backend_raw, dict):
            raise ValueError("backend must be a mapping")
        url = str(backend_raw.get("url") or "").rstrip("/")
        if url:
            backend_cfg = BackendConfig(url=url)

    node_id = str(raw["node_id"])
    if not mqtt_cfg.client_id:
        mqtt_cfg.client_id = node_id

    return NodeConfig(
        node_id=node_id,
        mqtt=mqtt_cfg,
        sensors=sensors,
        poll_interval=int(raw.get("poll_interval", 30)),
        cameras=cameras,
        backend=backend_cfg,
    )
