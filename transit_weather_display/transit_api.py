"""Mock transit data provider."""

from __future__ import annotations

from typing import List

try:
    from .models import TrainArrival
except ImportError:
    from models import TrainArrival


def get_train_data() -> List[TrainArrival]:
    """Return mocked train arrival data."""

    return [
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
    ]
