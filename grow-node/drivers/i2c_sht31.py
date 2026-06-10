from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseSensor, SensorReading

if TYPE_CHECKING:
    from config import SensorConfig

try:
    import board
    import busio
    import adafruit_sht31d
    _SHT31_AVAILABLE = True
except ImportError:
    _SHT31_AVAILABLE = False

_VALID_ADDRESSES = (0x44, 0x45)


class I2cSht31Sensor(BaseSensor):
    def __init__(self, config: SensorConfig) -> None:
        if not _SHT31_AVAILABLE:
            raise RuntimeError(
                f"Sensor '{config.id}': adafruit-circuitpython-sht31d is not installed. "
                "On Raspberry Pi, install with: pip install -r requirements-pi.txt"
            )
        super().__init__(config)

        address = config.params.get("address")
        if address is None:
            raise ValueError(f"Sensor '{config.id}': 'address' is required (0x44 or 0x45)")
        address = int(address)
        if address not in _VALID_ADDRESSES:
            raise ValueError(
                f"Sensor '{config.id}': address must be 0x44 or 0x45, got {hex(address)}"
            )

        i2c = busio.I2C(board.SCL, board.SDA)
        self._sensor = adafruit_sht31d.SHT31D(i2c, address=address)

    def read(self) -> SensorReading:
        try:
            temp = self._sensor.temperature
            humidity = self._sensor.relative_humidity
            if temp is None or humidity is None:
                raise RuntimeError("SHT31-D returned None")
            return {
                "temperature": round(float(temp), 2),
                "humidity": round(float(humidity), 2),
            }
        except Exception as e:
            raise RuntimeError(f"Sensor '{self.sensor_id}': read failed — {e}") from e
