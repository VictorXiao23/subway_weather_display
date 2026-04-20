# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
python -m transit_weather_display.main
```

Requires Pillow (`pip install Pillow`). API keys and location config go in `.env` (see `.env` for format — `METEOSOURCE_API_KEY`, `WEATHER_LAT`, `WEATHER_LON`, etc.).

## Architecture

This is a Python e-paper display app that renders real-time NYC subway arrivals and weather onto an 800×400 monochrome image, intended to run on embedded hardware.

**Data flow:**
1. `main.py` runs a 60s refresh loop with a `DataCache` that tracks independent refresh intervals: trains every 60s, weather every 15 min.
2. `transit_api.py` and `weather_api.py` fetch data → frozen dataclasses in `models.py` (`TrainArrival`, `WeatherData`, `DisplayData`).
3. `display.py` renders a PIL `Image` (1-bit monochrome) from `DisplayData`.
4. On hardware, replace `image.show()` in `main.py` with `epd.display(image)`.

**Key files:**
- `config.py` — all display constants and `.env` loader; change layout dimensions, refresh intervals, or font sizes here.
- `display.py` — all UI rendering logic (800+ lines); left panel is trains, right panel is weather.
- `transit_api.py` — currently returns **hardcoded mock data**; real MTA API integration goes here.
- `weather_api.py` — Meteosource API; returns safe fallback `WeatherData` on network errors.

## Transit Data

`transit_api.py` is a stub with mock F/G/A line data. To integrate a real MTA feed, implement `get_train_data() -> list[TrainArrival]` using the same return type — the rest of the pipeline will work unchanged.
