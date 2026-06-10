from __future__ import annotations

import time
from typing import TYPE_CHECKING

from .base import BaseSensor, SensorReading

if TYPE_CHECKING:
    from config import SensorConfig

try:
    import board
    import adafruit_dht
    _DHT_AVAILABLE = True
except ImportError:
    _DHT_AVAILABLE = False

# GPIO pin number → board attribute name
_PIN_MAP: dict[int, str] = {
    4: "D4", 17: "D17", 18: "D18", 22: "D22", 23: "D23",
    24: "D24", 25: "D25", 27: "D27",
}


class GpioDht22Sensor(BaseSensor):
    def __init__(self, config: SensorConfig) -> None:
        if not _DHT_AVAILABLE:
            raise RuntimeError(
                f"Sensor '{config.id}': adafruit-circuitpython-dht is not installed. "
                "On Raspberry Pi, install with: pip install -r requirements-pi.txt"
            )
        super().__init__(config)

        pin_num = config.params.get("pin")
        if pin_num is None:
            raise ValueError(f"Sensor '{config.id}': 'pin' is required for gpio interface")

        pin_name = _PIN_MAP.get(int(pin_num))
        if pin_name is None:
            supported = sorted(_PIN_MAP.keys())
            raise ValueError(
                f"Sensor '{config.id}': GPIO pin {pin_num} not supported. "
                f"Supported pins: {supported}"
            )

        board_pin = getattr(board, pin_name)
        # use_pulseio=False avoids requiring elevated permissions on most Pi setups
        self._device = adafruit_dht.DHT22(board_pin, use_pulseio=False)
        self._retries = int(config.params.get("retries", 3))
        self._retry_delay = float(config.params.get("retry_delay", 0.5))

    def read(self) -> SensorReading:
        last_exc: Exception | None = None
        for attempt in range(self._retries):
            try:
                temp = self._device.temperature
                humidity = self._device.humidity
                if temp is None or humidity is None:
                    raise RuntimeError("DHT22 returned None")
                return {
                    "temperature": round(float(temp), 1),
                    "humidity": round(float(humidity), 1),
                }
            except RuntimeError as e:
                last_exc = e
                if attempt < self._retries - 1:
                    time.sleep(self._retry_delay)
        raise RuntimeError(
            f"Sensor '{self.sensor_id}': failed after {self._retries} attempts: {last_exc}"
        )
