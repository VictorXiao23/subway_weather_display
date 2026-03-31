"""Application configuration constants."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"


def _load_local_env(env_file: Path) -> None:
    """Load simple KEY=VALUE pairs from a local .env file into os.environ."""

    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")

        if key:
            os.environ.setdefault(key, value)


_load_local_env(ENV_FILE)


# Display configuration
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 400
DISPLAY_BACKGROUND = "white"
DISPLAY_FOREGROUND = "black"

# Refresh behavior
REFRESH_INTERVAL_SECONDS = 60
TRAIN_REFRESH_INTERVAL_SECONDS = 60
WEATHER_REFRESH_INTERVAL_SECONDS = 15 * 60

# Layout configuration
SCREEN_PADDING = 24
SECTION_GAP = 16
TRAIN_ROW_HEIGHT = 40
FORECAST_ITEM_WIDTH = 100
FORECAST_ITEM_GAP = 12
DIVIDER_THICKNESS = 1

# Typography
FONT_LARGE_SIZE = 44
FONT_MEDIUM_SIZE = 26
FONT_SMALL_SIZE = 18

# Content limits
MAX_TRAIN_ROWS = 3
MAX_FORECAST_HOURS = 6
