from __future__ import annotations

import logging
import sys

from camera_manager import CameraManager
from config import load_config
from publisher import run_publish_loop


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )


def main() -> None:
    setup_logging()
    log = logging.getLogger(__name__)

    config_path = "config.yaml"
    log.info("Loading config from %s", config_path)
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        log.error("Config file not found: %s", config_path)
        sys.exit(1)
    except ValueError as e:
        log.error("Config error: %s", e)
        sys.exit(1)

    log.info(
        "Node '%s' — %d sensor(s), %d camera(s), broker=%s:%d, interval=%ds",
        config.node_id, len(config.sensors), len(config.cameras),
        config.mqtt.broker, config.mqtt.port, config.poll_interval,
    )

    camera_manager = None
    if config.cameras:
        camera_manager = CameraManager(config.cameras)
        camera_manager.start()

    try:
        run_publish_loop(config)
    finally:
        if camera_manager:
            camera_manager.stop()


if __name__ == "__main__":
    main()
