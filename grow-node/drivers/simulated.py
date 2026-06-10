from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .base import BaseSensor, SensorReading

if TYPE_CHECKING:
    from config import SensorConfig


class SimulatedSensor(BaseSensor):
    def __init__(self, config: SensorConfig) -> None:
        super().__init__(config)
        p = config.params
        self._temp_min = float(p.get("temp_min", 20.0))
        self._temp_max = float(p.get("temp_max", 30.0))
        self._humidity_min = float(p.get("humidity_min", 40.0))
        self._humidity_max = float(p.get("humidity_max", 80.0))
        if self._temp_min >= self._temp_max:
            raise ValueError(f"Sensor '{config.id}': temp_min must be < temp_max")
        if self._humidity_min >= self._humidity_max:
            raise ValueError(f"Sensor '{config.id}': humidity_min must be < humidity_max")

    def read(self) -> SensorReading:
        return {
            "temperature": round(random.uniform(self._temp_min, self._temp_max), 1),
            "humidity": round(random.uniform(self._humidity_min, self._humidity_max), 1),
        }
