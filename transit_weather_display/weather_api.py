"""Live weather data provider."""

from __future__ import annotations

import gzip
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from .config import MAX_FORECAST_HOURS, DeviceConfig
    from .models import WeatherData
except ImportError:
    from config import MAX_FORECAST_HOURS, DeviceConfig
    from models import WeatherData


METEOSOURCE_BASE_URL = "https://www.meteosource.com/api/v1/free/point"
METEOSOURCE_API_KEY = os.getenv("METEOSOURCE_API_KEY", "")
WEATHER_LANGUAGE = os.getenv("WEATHER_LANGUAGE", "en")
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "us")


def _unavailable_weather_data() -> WeatherData:
    """Return a neutral weather state when live data is unavailable."""

    return WeatherData(
        temp=None,
        condition="Unavailable",
        hourly=[],
    )


def _build_request_url(config: DeviceConfig) -> str:
    """Build the Meteosource point forecast URL."""

    params = {
        "key": METEOSOURCE_API_KEY,
        "lat": config.weather_lat,
        "lon": config.weather_lon,
        "sections": "current,hourly",
        "timezone": config.weather_timezone,
        "language": WEATHER_LANGUAGE,
        "units": WEATHER_UNITS,
    }
    return f"{METEOSOURCE_BASE_URL}?{urlencode(params)}"


def _parse_weather_payload(payload: dict[str, Any]) -> WeatherData:
    """Parse the Meteosource response into the renderer's weather model."""

    current = payload.get("current", {})
    hourly_section = payload.get("hourly", {})
    hourly_data = hourly_section.get("data", [])

    current_temp = round(current.get("temperature", 0))
    condition = (
        current.get("summary")
        or current.get("weather")
        or current.get("icon")
        or "Unavailable"
    )
    hourly_temps = [
        round(entry.get("temperature", current_temp))
        for entry in hourly_data[:MAX_FORECAST_HOURS]
    ]

    return WeatherData(
        temp=current_temp,
        condition=condition,
        hourly=hourly_temps,
    )


def _fetch_live_weather(config: DeviceConfig) -> WeatherData:
    """Fetch weather data from Meteosource."""

    if not METEOSOURCE_API_KEY:
        raise ValueError("Missing METEOSOURCE_API_KEY")

    request = Request(
        _build_request_url(config),
        headers={
            "Accept": "application/json",
            "User-Agent": "transit-weather-display/1.0",
        },
    )

    with urlopen(request, timeout=10) as response:
        raw_body = response.read()
        if response.headers.get("Content-Encoding", "").lower() == "gzip":
            raw_body = gzip.decompress(raw_body)
        payload = json.loads(raw_body.decode("utf-8"))
    return _parse_weather_payload(payload)


def get_weather_data(config: DeviceConfig) -> WeatherData:
    """Return live weather data when configured, otherwise mark weather unavailable."""

    try:
        return _fetch_live_weather(config)
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return _unavailable_weather_data()
