"""Mock weather data provider."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from .config import (
        MAX_FORECAST_HOURS,
        METEOSOURCE_API_KEY,
        METEOSOURCE_BASE_URL,
        WEATHER_LANGUAGE,
        WEATHER_LAT,
        WEATHER_LON,
        WEATHER_TIMEZONE,
        WEATHER_UNITS,
    )
    from .models import WeatherData
except ImportError:
    from config import (
        MAX_FORECAST_HOURS,
        METEOSOURCE_API_KEY,
        METEOSOURCE_BASE_URL,
        WEATHER_LANGUAGE,
        WEATHER_LAT,
        WEATHER_LON,
        WEATHER_TIMEZONE,
        WEATHER_UNITS,
    )
    from models import WeatherData


def _mock_weather_data() -> WeatherData:
    """Return fallback weather data when the live API is unavailable."""

    return WeatherData(
        temp=36,
        condition="Cloudy",
        hourly=[33, 33, 32, 32, 31, 31, 30, 30],
    )


def _build_request_url() -> str:
    """Build the Meteosource point forecast URL."""

    params = {
        "lat": WEATHER_LAT,
        "lon": WEATHER_LON,
        "sections": "current,hourly",
        "timezone": WEATHER_TIMEZONE,
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
    condition = current.get("summary") or current.get("icon") or "Unavailable"
    hourly_temps = [
        round(entry.get("temperature", current_temp))
        for entry in hourly_data[:MAX_FORECAST_HOURS]
    ]

    if not hourly_temps:
        hourly_temps = _mock_weather_data().hourly[:MAX_FORECAST_HOURS]

    return WeatherData(
        temp=current_temp,
        condition=condition,
        hourly=hourly_temps,
    )


def _fetch_live_weather() -> WeatherData:
    """Fetch weather data from Meteosource."""

    if not METEOSOURCE_API_KEY:
        raise ValueError("Missing METEOSOURCE_API_KEY")

    request = Request(
        _build_request_url(),
        headers={
            "X-API-Key": METEOSOURCE_API_KEY,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "User-Agent": "transit-weather-display/1.0",
        },
    )

    with urlopen(request, timeout=10) as response:
        payload = json.load(response)
    return _parse_weather_payload(payload)


def get_weather_data() -> WeatherData:
    """Return live weather data when configured, otherwise fall back to mock data."""

    try:
        return _fetch_live_weather()
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return _mock_weather_data()
