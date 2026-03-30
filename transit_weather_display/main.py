"""Application entry point for the transit and weather e-paper display."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Optional

try:
    from .config import (
        REFRESH_INTERVAL_SECONDS,
        TRAIN_REFRESH_INTERVAL_SECONDS,
        WEATHER_REFRESH_INTERVAL_SECONDS,
    )
    from .display import render_ui
    from .models import DisplayData, TrainArrival, WeatherData
    from .transit_api import get_train_data
    from .weather_api import get_weather_data
except ImportError:
    from config import (
        REFRESH_INTERVAL_SECONDS,
        TRAIN_REFRESH_INTERVAL_SECONDS,
        WEATHER_REFRESH_INTERVAL_SECONDS,
    )
    from display import render_ui
    from models import DisplayData, TrainArrival, WeatherData
    from transit_api import get_train_data
    from weather_api import get_weather_data


class DataCache:
    """Tracks the most recent API results and their refresh timestamps."""

    def __init__(self) -> None:
        self.trains: list[TrainArrival] = []
        self.weather: Optional[WeatherData] = None
        self.last_train_fetch = 0.0
        self.last_weather_fetch = 0.0


def _should_refresh(last_fetch: float, interval_seconds: int, now: float) -> bool:
    """Return True when cached data should be refreshed."""

    return last_fetch == 0.0 or (now - last_fetch) >= interval_seconds


def _get_cached_trains(cache: DataCache, now: float) -> list[TrainArrival]:
    """Refresh train data when its interval has elapsed."""

    if _should_refresh(cache.last_train_fetch, TRAIN_REFRESH_INTERVAL_SECONDS, now):
        cache.trains = get_train_data()
        cache.last_train_fetch = now
    return cache.trains


def _get_cached_weather(cache: DataCache, now: float) -> WeatherData:
    """Refresh weather data when its interval has elapsed."""

    if cache.weather is None or _should_refresh(
        cache.last_weather_fetch,
        WEATHER_REFRESH_INTERVAL_SECONDS,
        now,
    ):
        cache.weather = get_weather_data()
        cache.last_weather_fetch = now
    return cache.weather


def build_display_data(cache: DataCache) -> DisplayData:
    """Fetch cached data sources and build the UI view model."""

    loop_time = time.monotonic()

    return DisplayData(
        timestamp=datetime.now(),
        trains=_get_cached_trains(cache, loop_time),
        weather=_get_cached_weather(cache, loop_time),
    )


def main() -> None:
    """Run the passive display refresh loop."""

    cache = DataCache()

    while True:
        display_data = build_display_data(cache)
        image = render_ui(display_data)

        # Placeholder for future hardware integration, e.g. epd.display(image)
        image.show()
        time.sleep(REFRESH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
