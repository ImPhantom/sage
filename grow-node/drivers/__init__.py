from __future__ import annotations

from .base import BaseSensor, SensorReading
from .simulated import SimulatedSensor

REGISTRY: dict[str, type[BaseSensor]] = {
    "simulated": SimulatedSensor,
}

try:
    from .gpio_dht22 import GpioDht22Sensor
    REGISTRY["gpio"] = GpioDht22Sensor
except (ImportError, RuntimeError):
    pass  # Adafruit libs not available; gpio sensors raise at startup if configured

try:
    from .ble_tp358 import BleTp358Sensor
    REGISTRY["bluetooth"] = BleTp358Sensor
except (ImportError, RuntimeError):
    pass

try:
    from .i2c_sht31 import I2cSht31Sensor
    REGISTRY["i2c"] = I2cSht31Sensor
except (ImportError, RuntimeError):
    pass

__all__ = ["REGISTRY", "BaseSensor", "SensorReading"]
