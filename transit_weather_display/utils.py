"""Utility helpers shared across modules."""

from __future__ import annotations

from datetime import datetime, timedelta


def format_clock(timestamp: datetime) -> str:
    """Format time for a large, readable display heading."""

    return timestamp.strftime("%-I:%M %p")


def format_date(timestamp: datetime) -> str:
    """Format the current date for the top header."""

    return timestamp.strftime("%a, %b %-d")


def format_train_eta(minutes: int) -> str:
    """Convert minute values into short arrival text."""

    if minutes <= 0:
        return "Now"
    return f"{minutes} min"


def format_temperature(value: int | None) -> str:
    """Render temperatures consistently across the UI."""

    if value is None:
        return "--"
    return f"{value}\N{DEGREE SIGN}"


def format_arrival_clock(timestamp: datetime, minutes: int) -> str:
    """Format an arrival clock time based on minutes from now."""

    arrival_time = timestamp + timedelta(minutes=max(0, minutes))
    return arrival_time.strftime("%-I:%M")


def format_forecast_hour(timestamp: datetime, hours_ahead: int) -> str:
    """Format a forecast slot label using actual clock time."""

    forecast_time = timestamp + timedelta(hours=max(0, hours_ahead))
    return forecast_time.strftime("%-I %p").lower()
