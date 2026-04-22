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
DISPLAY_HEIGHT = 480
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
MAX_TRAIN_ROWS = 4
MAX_FORECAST_HOURS = 8

# MTA API
MTA_API_KEY = os.environ.get("MTA_API_KEY", "")

# Comma-separated feed URLs to fetch (paste directly from MTA developer portal)
# Example: MTA_FEED_URLS=https://api-endpoint.mta.info/.../gtfs-bdfm,https://api-endpoint.mta.info/.../gtfs-g
MTA_FEED_URLS: list[str] = [
    u.strip()
    for u in os.environ.get("MTA_FEED_URLS", "").split(",")
    if u.strip()
]


def _parse_subway_stops(raw: str) -> list[dict]:
    # Format: stop_id:north_label:south_label[:lines]
    # lines is optional comma-separated list, e.g. "4,5" — omit to allow all lines
    # Multiple stops separated by |
    stops = []
    for part in raw.split("|"):
        part = part.strip()
        if not part:
            continue
        fields = part.split(":")
        if len(fields) < 3:
            continue
        stop_id, north, south = fields[0], fields[1], fields[2]
        lines = {l.strip().upper() for l in fields[3].split(",")} if len(fields) >= 4 else set()
        stops.append({
            "stop_id": stop_id.strip(),
            "north": north.strip(),
            "south": south.strip(),
            "lines": lines,
        })
    return stops


SUBWAY_STOPS = _parse_subway_stops(
    os.environ.get("SUBWAY_STOPS", "F20:Manhattan:Brooklyn")
)
