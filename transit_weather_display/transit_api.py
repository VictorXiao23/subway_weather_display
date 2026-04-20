"""Mock transit data provider."""

from __future__ import annotations

from typing import List

try:
    from .config import DeviceConfig
    from .models import TrainArrival
except ImportError:
    from config import DeviceConfig
    from models import TrainArrival


_MOCK_ARRIVALS: List[TrainArrival] = [
    TrainArrival(line="F", minutes=3, destination="Manhattan"),
    TrainArrival(line="F", minutes=8, destination="Manhattan"),
    TrainArrival(line="F", minutes=5, destination="Brooklyn"),
    TrainArrival(line="F", minutes=12, destination="Brooklyn"),
    TrainArrival(line="G", minutes=5, destination="Brooklyn"),
    TrainArrival(line="G", minutes=11, destination="Brooklyn"),
    TrainArrival(line="G", minutes=4, destination="Queens"),
    TrainArrival(line="G", minutes=13, destination="Queens"),
    TrainArrival(line="A", minutes=7, destination="Uptown"),
    TrainArrival(line="A", minutes=15, destination="Uptown"),
    TrainArrival(line="A", minutes=6, destination="Downtown"),
    TrainArrival(line="A", minutes=14, destination="Downtown"),
    TrainArrival(line="C", minutes=4, destination="Uptown"),
    TrainArrival(line="C", minutes=10, destination="Uptown"),
    TrainArrival(line="C", minutes=3, destination="Downtown"),
    TrainArrival(line="C", minutes=9, destination="Downtown"),
    TrainArrival(line="E", minutes=6, destination="Uptown"),
    TrainArrival(line="E", minutes=14, destination="Uptown"),
]


def get_train_data(config: DeviceConfig) -> List[TrainArrival]:
    """Return mocked train arrival data filtered to the configured lines.

    When integrating a real MTA feed, replace the mock list with live API
    calls — the filtering and return type stay the same.
    """

    if not config.train_lines:
        return list(_MOCK_ARRIVALS)
    allowed = set(config.train_lines)
    return [t for t in _MOCK_ARRIVALS if t.line in allowed]
