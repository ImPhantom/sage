import logging
import os

import httpx

logger = logging.getLogger(__name__)

_GO2RTC_URL = os.environ.get("GO2RTC_URL", "http://go2rtc:1984")

_cameras: dict[str, list[dict]] = {}


def register_stream(name: str, rtsp_url: str) -> None:
    try:
        r = httpx.put(f"{_GO2RTC_URL}/api/streams?name={name}&src={rtsp_url}", timeout=5)
        if r.status_code != 400:
            r.raise_for_status()
    except Exception as e:
        logger.warning("go2rtc register failed for %s: %s", name, e)


def deregister_stream(name: str) -> None:
    try:
        r = httpx.delete(f"{_GO2RTC_URL}/api/streams?name={name}", timeout=5)
        r.raise_for_status()
    except Exception as e:
        logger.warning("go2rtc deregister failed for %s: %s", name, e)


def register_node_cameras(node_id: str, cameras: list[dict]) -> None:
    _cameras[node_id] = cameras
    for cam in cameras:
        register_stream(f"{node_id}_{cam['id']}", cam["rtsp_url"])


def replay_registrations() -> None:
    for node_id, cameras in _cameras.items():
        for cam in cameras:
            register_stream(f"{node_id}_{cam['id']}", cam["rtsp_url"])


def get_cameras() -> dict[str, list[dict]]:
    return _cameras
