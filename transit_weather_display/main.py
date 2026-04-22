"""Application entry point for the transit and weather e-paper display."""

from __future__ import annotations

import time
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image

try:
    from waveshare_epd import epd7in5_V2 as _epd_module
    _HARDWARE = True
except ImportError:
    _HARDWARE = False


def _show(image: Image.Image) -> None:
    if _HARDWARE:
        epd = _epd_module.EPD()
        epd.init()
        epd.display(epd.getbuffer(image))
        epd.sleep()
    else:
        image.show()

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


NEW_YORK_TZ = ZoneInfo("America/New_York")


class DataCache:
    def __init__(self) -> None:
        self.trains: list[TrainArrival] = []
        self.weather: WeatherData | None = None
        self.last_train_fetch = 0.0
        self.last_weather_fetch = 0.0


def _should_refresh(last_fetch: float, interval_seconds: int, now: float) -> bool:
    return last_fetch == 0.0 or (now - last_fetch) >= interval_seconds


def _get_cached_trains(cache: DataCache, now: float) -> list[TrainArrival]:
    if _should_refresh(cache.last_train_fetch, TRAIN_REFRESH_INTERVAL_SECONDS, now):
        cache.trains = get_train_data()
        cache.last_train_fetch = now
    return cache.trains


def _get_cached_weather(cache: DataCache, now: float) -> WeatherData:
    if cache.weather is None or _should_refresh(
        cache.last_weather_fetch, WEATHER_REFRESH_INTERVAL_SECONDS, now
    ):
        cache.weather = get_weather_data()
        cache.last_weather_fetch = now
    return cache.weather


def build_display_data(cache: DataCache) -> DisplayData:
    now = time.monotonic()
    return DisplayData(
        timestamp=datetime.now(NEW_YORK_TZ),
        trains=_get_cached_trains(cache, now),
        weather=_get_cached_weather(cache, now),
    )


def main() -> None:
    cache = DataCache()

    while True:
        display_data = build_display_data(cache)
        image = render_ui(display_data)

        _show(image)
        time.sleep(REFRESH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
