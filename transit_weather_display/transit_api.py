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
        TrainArrival(line="F", minutes=16, destination="Manhattan"),
        TrainArrival(line="G", minutes=5, destination="Brooklyn"),
        TrainArrival(line="G", minutes=12, destination="Brooklyn"),
        TrainArrival(line="G", minutes=22, destination="Brooklyn"),
    ]
