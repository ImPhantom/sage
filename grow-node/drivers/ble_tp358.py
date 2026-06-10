from __future__ import annotations

import asyncio
import struct
from typing import TYPE_CHECKING

from .base import BaseSensor, SensorReading

if TYPE_CHECKING:
    from config import SensorConfig

try:
    from bleak import BleakScanner
    _BLEAK_AVAILABLE = True
except ImportError:
    _BLEAK_AVAILABLE = False


class BleTp358Sensor(BaseSensor):
    def __init__(self, config: SensorConfig) -> None:
        if not _BLEAK_AVAILABLE:
            raise RuntimeError(
                f"Sensor '{config.id}': bleak is not installed. "
                "Install with: pip install bleak"
            )
        super().__init__(config)
        mac = config.params.get("mac")
        if not mac:
            raise ValueError(f"Sensor '{config.id}': 'mac' is required for bluetooth interface")
        self._mac = str(mac).upper()
        self._scan_timeout = float(config.params.get("scan_timeout", 10.0))

    def read(self) -> SensorReading:
        try:
            return asyncio.run(self._scan())
        except RuntimeError as e:
            raise RuntimeError(f"Sensor '{self.sensor_id}': {e}") from e

    async def _scan(self) -> SensorReading:
        found = asyncio.Event()
        result: SensorReading = {}

        def _callback(device, adv):
            if device.address.upper() != self._mac:
                return
            mfr = adv.manufacturer_data
            if not mfr:
                return
            last_id = list(mfr)[-1]
            data = int(last_id).to_bytes(2, byteorder="little") + mfr[last_id]
            if len(data) < 5:
                return
            temp_humi = data[1:4]
            if temp_humi == b"\xff\xff\xff":
                return
            temp_raw, humidity = struct.unpack("<hB", temp_humi)
            result["temperature"] = round(temp_raw / 10.0, 1)
            result["humidity"] = float(humidity)
            found.set()

        async with BleakScanner(_callback):
            try:
                await asyncio.wait_for(found.wait(), timeout=self._scan_timeout)
            except asyncio.TimeoutError:
                raise RuntimeError(
                    f"No advertisement received from {self._mac} within {self._scan_timeout}s"
                )
        return result
