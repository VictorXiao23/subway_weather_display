"""Application configuration constants."""

import os
from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class DeviceConfig:
    """Per-device configuration: which trains to show and where to fetch weather."""

    name: str
    weather_lat: str
    weather_lon: str
    weather_timezone: str
    train_lines: list[str] = field(default_factory=list)


# Named device configurations — add or edit entries here for each physical device.
DEVICE_CONFIGS: dict[str, DeviceConfig] = {
    "brooklyn": DeviceConfig(
        name="Brooklyn",
        weather_lat="40.6782",
        weather_lon="-73.9442",
        weather_timezone="America/New_York",
        train_lines=["F", "G"],
    ),
    "manhattan": DeviceConfig(
        name="Manhattan",
        weather_lat="40.7580",
        weather_lon="-73.9855",
        weather_timezone="America/New_York",
        train_lines=["A", "C", "E"],
    ),
}

_DEFAULT_DEVICE_ID = "brooklyn"


def get_device_config() -> DeviceConfig:
    """Return the DeviceConfig selected by the DEVICE_ID environment variable."""

    device_id = os.getenv("DEVICE_ID", _DEFAULT_DEVICE_ID).lower()
    if device_id not in DEVICE_CONFIGS:
        known = ", ".join(DEVICE_CONFIGS)
        raise ValueError(f"Unknown DEVICE_ID={device_id!r}. Known devices: {known}")
    return DEVICE_CONFIGS[device_id]


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
