from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import yaml

from config import CameraConfig

log = logging.getLogger(__name__)

_GENERATED_CONFIG_PATH = "/tmp/mediamtx_generated.yaml"


class CameraManager:
    def __init__(self, cameras: list[CameraConfig]) -> None:
        self._cameras = cameras
        self._proc: Optional[subprocess.Popen] = None  # type: ignore[type-arg]

    def start(self) -> None:
        config_path = _GENERATED_CONFIG_PATH
        mediamtx_cfg = self._generate_config()
        Path(config_path).write_text(yaml.dump(mediamtx_cfg, default_flow_style=False))
        log.info("mediamtx config written to %s (%d path(s))", config_path, len(self._cameras))

        self._proc = subprocess.Popen(["mediamtx", config_path])
        log.info("mediamtx spawned (pid=%d)", self._proc.pid)

        if self._proc.poll() is not None:
            log.warning("mediamtx exited immediately — check config at %s", config_path)

    def stop(self) -> None:
        if self._proc is None or self._proc.poll() is not None:
            return
        log.info("Stopping mediamtx (pid=%d)", self._proc.pid)
        self._proc.terminate()
        try:
            self._proc.wait(timeout=5)
            log.info("mediamtx stopped")
        except subprocess.TimeoutExpired:
            log.warning("mediamtx did not stop within 5s — sending SIGKILL")
            self._proc.kill()
            self._proc.wait()

    def _generate_config(self) -> dict:
        paths = {}
        for cam in self._cameras:
            paths[cam.id] = self._build_path_entry(cam)
        return {"logLevel": "info", "paths": paths}

    def _build_path_entry(self, camera: CameraConfig) -> dict:
        if camera.type == "rpi_csi":
            return {
                "source": "rpiCamera",
                "rpiCameraID": int(camera.params["camera_id"]),
            }
        if camera.type == "usb":
            device = camera.params["device"]
            rtsp_url = f"rtsp://localhost:8554/{camera.id}"
            return {
                "runOnInit": (
                    f"ffmpeg -f v4l2 -i {device} -c:v libx264 -preset ultrafast -f rtsp {rtsp_url}"
                ),
                "runOnInitRestart": True,
            }
        if camera.type == "rtsp":
            return {"source": camera.params["url"]}
        raise ValueError(f"Unknown camera type: {camera.type!r}")
