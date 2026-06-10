from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from config import SensorConfig


class SensorReading(TypedDict, total=False):
    temperature: float
    humidity: float
    co2: float


class BaseSensor(ABC):
    def __init__(self, config: SensorConfig) -> None:
        self.sensor_id = config.id
        self.sensor_type = config.type

    @abstractmethod
    def read(self) -> SensorReading:
        """Read sensor values. Returns only the metrics this sensor measures.
        Raises RuntimeError on hardware failure."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.sensor_id!r})"
