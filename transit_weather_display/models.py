from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrainArrival:
    line: str
    minutes: int
    destination: str


@dataclass(frozen=True)
class WeatherData:
    temp: int | None
    condition: str
    hourly: list[int]


@dataclass(frozen=True)
class DisplayData:
    timestamp: datetime
    trains: list[TrainArrival]
    weather: WeatherData
