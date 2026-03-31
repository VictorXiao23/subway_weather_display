"""Shared data models for the display application."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class TrainArrival:
    """Represents a single train arrival prediction."""

    line: str
    minutes: int
    destination: str


@dataclass(frozen=True)
class WeatherData:
    """Represents the current weather and a short hourly forecast."""

    temp: Optional[int]
    condition: str
    hourly: List[int]


@dataclass(frozen=True)
class DisplayData:
    """Top-level view model consumed by the renderer."""

    timestamp: datetime
    trains: List[TrainArrival]
    weather: WeatherData
