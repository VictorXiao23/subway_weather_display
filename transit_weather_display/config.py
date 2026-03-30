"""Application configuration constants."""

import os
from pathlib import Path


# Display configuration
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 300
DISPLAY_BACKGROUND = "white"
DISPLAY_FOREGROUND = "black"

# Refresh behavior
REFRESH_INTERVAL_SECONDS = 60
TRAIN_REFRESH_INTERVAL_SECONDS = 60
WEATHER_REFRESH_INTERVAL_SECONDS = 15 * 60

# Layout configuration
SCREEN_PADDING = 16
SECTION_GAP = 10
TRAIN_ROW_HEIGHT = 30
FORECAST_ITEM_WIDTH = 62
FORECAST_ITEM_GAP = 8
DIVIDER_THICKNESS = 1

# Typography
FONT_LARGE_SIZE = 30
FONT_MEDIUM_SIZE = 18
FONT_SMALL_SIZE = 14

# Content limits
MAX_TRAIN_ROWS = 3
MAX_FORECAST_HOURS = 8

# Weather API configuration
METEOSOURCE_BASE_URL = "https://www.meteosource.com/api/v1/free/point"
METEOSOURCE_API_KEY = os.getenv("METEOSOURCE_API_KEY", "")
WEATHER_LAT = os.getenv("WEATHER_LAT", "40.6782")
WEATHER_LON = os.getenv("WEATHER_LON", "-73.9442")
WEATHER_TIMEZONE = os.getenv("WEATHER_TIMEZONE", "America/New_York")
WEATHER_LANGUAGE = os.getenv("WEATHER_LANGUAGE", "en")
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "us")

# Assets
BASE_DIR = Path(__file__).resolve().parent
