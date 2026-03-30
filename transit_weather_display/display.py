"""UI rendering for the 400x300 monochrome e-paper display."""

from __future__ import annotations

from collections import OrderedDict
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

try:
    from .config import (
        DISPLAY_BACKGROUND,
        DISPLAY_FOREGROUND,
        DISPLAY_HEIGHT,
        DISPLAY_WIDTH,
        DIVIDER_THICKNESS,
        FONT_LARGE_SIZE,
        FONT_MEDIUM_SIZE,
        FONT_SMALL_SIZE,
        FORECAST_ITEM_GAP,
        FORECAST_ITEM_WIDTH,
        MAX_FORECAST_HOURS,
        MAX_TRAIN_ROWS,
        SCREEN_PADDING,
        SECTION_GAP,
        TRAIN_ROW_HEIGHT,
    )
    from .models import DisplayData
    from .utils import (
        format_arrival_clock,
        format_clock,
        format_date,
        format_forecast_hour,
        format_temperature,
        format_train_eta,
    )
except ImportError:
    from config import (
        DISPLAY_BACKGROUND,
        DISPLAY_FOREGROUND,
        DISPLAY_HEIGHT,
        DISPLAY_WIDTH,
        DIVIDER_THICKNESS,
        FONT_LARGE_SIZE,
        FONT_MEDIUM_SIZE,
        FONT_SMALL_SIZE,
        FORECAST_ITEM_GAP,
        FORECAST_ITEM_WIDTH,
        MAX_FORECAST_HOURS,
        MAX_TRAIN_ROWS,
        SCREEN_PADDING,
        SECTION_GAP,
        TRAIN_ROW_HEIGHT,
    )
    from models import DisplayData
    from utils import (
        format_arrival_clock,
        format_clock,
        format_date,
        format_forecast_hour,
        format_temperature,
        format_train_eta,
    )


OUTER_MARGIN = 8
FRAME_INSET = 4
HEADER_HEIGHT = 38
RIGHT_PANEL_WIDTH = 124
LEFT_PANEL_MIN_WIDTH = 0
ROUTE_BADGE_SIZE = 34
TRAIN_BLOCK_HEIGHT = 96
TRAIN_BLOCK_GAP = 12
WEATHER_ICON_SIZE = 30
HOURLY_ROW_HEIGHT = 16
TRAIN_ROW_SPACING = 24
TRAIN_VALUE_FONT_SIZE = 22


def _measure_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
) -> tuple[int, int]:
    """Return width and height for text using the active draw context."""

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
) -> None:
    """Draw text centered within a rectangle."""

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = bottom - top
    x0, y0, x1, y1 = box
    x = x0 + ((x1 - x0 - text_width) // 2) - left
    y = y0 + ((y1 - y0 - text_height) // 2) - top
    draw.text((x, y), text, font=font, fill=fill)


def _draw_route_badge(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    line_label: str,
    font: ImageFont.ImageFont,
) -> None:
    """Draw a filled circular route badge inspired by subway signage."""

    radius = ROUTE_BADGE_SIZE // 2
    draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        fill=DISPLAY_FOREGROUND,
        outline=DISPLAY_FOREGROUND,
        width=1,
    )
    _draw_centered_text(
        draw,
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        line_label,
        font,
        DISPLAY_BACKGROUND,
    )


def _draw_cloud_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    """Draw a simple monochrome cloud icon."""

    draw.arc((x + 2, y + 10, x + 16, y + 24), 180, 360, fill=DISPLAY_FOREGROUND, width=2)
    draw.arc((x + 10, y + 4, x + 25, y + 20), 180, 360, fill=DISPLAY_FOREGROUND, width=2)
    draw.arc((x + 20, y + 9, x + 34, y + 24), 180, 360, fill=DISPLAY_FOREGROUND, width=2)
    draw.line((x + 7, y + 24, x + 29, y + 24), fill=DISPLAY_FOREGROUND, width=2)


def _draw_weather_icon(draw: ImageDraw.ImageDraw, x: int, y: int, condition: str) -> None:
    """Draw a compact weather icon based on the condition label."""

    normalized = condition.lower()
    if "sun" in normalized or "clear" in normalized:
        center_x = x + 16
        center_y = y + 16
        draw.ellipse((center_x - 8, center_y - 8, center_x + 8, center_y + 8), outline=DISPLAY_FOREGROUND, width=2)
        for offset in (-14, -10, 10, 14):
            draw.line((center_x + offset, center_y - 1, center_x + offset + (2 if offset > 0 else -2), center_y - 1), fill=DISPLAY_FOREGROUND, width=2)
            draw.line((center_x - 1, center_y + offset, center_x - 1, center_y + offset + (2 if offset > 0 else -2)), fill=DISPLAY_FOREGROUND, width=2)
        return

    if "rain" in normalized:
        _draw_cloud_icon(draw, x, y, WEATHER_ICON_SIZE)
        draw.line((x + 12, y + 27, x + 9, y + 33), fill=DISPLAY_FOREGROUND, width=2)
        draw.line((x + 19, y + 27, x + 16, y + 33), fill=DISPLAY_FOREGROUND, width=2)
        draw.line((x + 26, y + 27, x + 23, y + 33), fill=DISPLAY_FOREGROUND, width=2)
        return

    _draw_cloud_icon(draw, x, y, WEATHER_ICON_SIZE)


def _group_trains_by_line(trains) -> list[tuple[str, Sequence]]:
    """Group train arrivals by line while preserving input order."""

    grouped = OrderedDict()
    for train in trains:
        grouped.setdefault(train.line, []).append(train)
    return list(grouped.items())


def _draw_train_section(
    draw: ImageDraw.ImageDraw,
    line_label: str,
    arrivals: Sequence,
    timestamp,
    x: int,
    y: int,
    width: int,
    badge_font: ImageFont.ImageFont,
    body_font: ImageFont.ImageFont,
    small_font: ImageFont.ImageFont,
) -> None:
    """Draw one grouped train block with a route badge and three arrivals."""

    badge_center_x = x + (ROUTE_BADGE_SIZE // 2)
    badge_center_y = y + 46
    _draw_route_badge(draw, badge_center_x, badge_center_y, line_label, badge_font)

    meta_x = x + ROUTE_BADGE_SIZE + 16
    draw.text((meta_x, y + 2), arrivals[0].destination, font=small_font, fill=DISPLAY_FOREGROUND)

    for index, train in enumerate(arrivals[:3]):
        row_y = y + 18 + (index * TRAIN_ROW_SPACING)
        minutes_value = "0" if train.minutes <= 0 else str(train.minutes)
        minutes_width, _ = _measure_text(draw, minutes_value, body_font)
        minutes_x = meta_x + 4
        min_label_x = minutes_x + minutes_width + 2
        arrival_text = format_arrival_clock(timestamp, train.minutes)
        time_width, _ = _measure_text(draw, arrival_text, body_font)

        draw.text((minutes_x, row_y), minutes_value, font=body_font, fill=DISPLAY_FOREGROUND)
        draw.text((min_label_x, row_y + 5), "min", font=small_font, fill=DISPLAY_FOREGROUND)
        draw.text((x + width - time_width, row_y), arrival_text, font=body_font, fill=DISPLAY_FOREGROUND)

    draw.line((meta_x, y + TRAIN_BLOCK_HEIGHT - 2, x + width, y + TRAIN_BLOCK_HEIGHT - 2), fill=DISPLAY_FOREGROUND, width=1)


def _draw_hourly_list(
    draw: ImageDraw.ImageDraw,
    timestamp,
    temperatures: Sequence[int],
    x: int,
    y: int,
    width: int,
    label_font: ImageFont.ImageFont,
    value_font: ImageFont.ImageFont,
) -> None:
    """Draw a simple vertical list of four hourly temperatures."""

    for index, temp in enumerate(temperatures[:MAX_FORECAST_HOURS]):
        row_y = y + (index * HOURLY_ROW_HEIGHT)
        hour_label = format_forecast_hour(timestamp, index + 1)
        temp_label = format_temperature(temp)
        draw.text((x, row_y), hour_label, font=label_font, fill=DISPLAY_FOREGROUND)
        temp_width, _ = _measure_text(draw, temp_label, value_font)
        draw.text((x + width - temp_width, row_y - 1), temp_label, font=value_font, fill=DISPLAY_FOREGROUND)


def _load_font(size: int) -> ImageFont.ImageFont:
    """Load a clean sans-serif font with a safe fallback."""

    preferred_fonts = (
        "DejaVuSans.ttf",
        "Arial.ttf",
        "LiberationSans-Regular.ttf",
    )

    for font_name in preferred_fonts:
        try:
            return ImageFont.truetype(font_name, size=size)
        except OSError:
            continue

    return ImageFont.load_default()


def render_ui(data: DisplayData) -> Image.Image:
    """Render the complete display UI and return a PIL image."""

    image = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), DISPLAY_BACKGROUND)
    draw = ImageDraw.Draw(image)

    large_font = _load_font(FONT_LARGE_SIZE)
    medium_font = _load_font(FONT_MEDIUM_SIZE)
    small_font = _load_font(FONT_SMALL_SIZE)
    train_value_font = _load_font(TRAIN_VALUE_FONT_SIZE)

    frame = (
        OUTER_MARGIN,
        OUTER_MARGIN,
        DISPLAY_WIDTH - OUTER_MARGIN,
        DISPLAY_HEIGHT - OUTER_MARGIN,
    )
    draw.rectangle(frame, outline=DISPLAY_FOREGROUND, width=1)

    inner_left = frame[0] + FRAME_INSET
    inner_top = frame[1] + FRAME_INSET
    inner_right = frame[2] - FRAME_INSET
    inner_bottom = frame[3] - FRAME_INSET
    header_bottom = inner_top + HEADER_HEIGHT
    right_panel_x = inner_right - RIGHT_PANEL_WIDTH

    left_panel_width = max(LEFT_PANEL_MIN_WIDTH, right_panel_x - inner_left)

    # Outer guides
    draw.line((inner_left, header_bottom, inner_right, header_bottom), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((right_panel_x, header_bottom, right_panel_x, inner_bottom), fill=DISPLAY_FOREGROUND, width=1)

    # Header
    date_text = format_date(data.timestamp)
    time_text = format_clock(data.timestamp).lower()
    date_width, _ = _measure_text(draw, date_text, medium_font)
    draw.text((inner_left + 10, inner_top + 8), date_text, font=medium_font, fill=DISPLAY_FOREGROUND)
    divider_x = inner_left + 10 + date_width + 12
    draw.line((divider_x, inner_top + 6, divider_x, header_bottom - 7), fill=DISPLAY_FOREGROUND, width=1)
    draw.text((divider_x + 12, inner_top + 8), time_text, font=medium_font, fill=DISPLAY_FOREGROUND)

    # Left transit panel
    trains_area_top = header_bottom + 10
    section_label = "Train Arrivals"
    draw.text((inner_left + 10, trains_area_top), section_label, font=small_font, fill=DISPLAY_FOREGROUND)

    train_start_y = trains_area_top + 16
    grouped_trains = _group_trains_by_line(data.trains)
    for index, (line_label, arrivals) in enumerate(grouped_trains[:MAX_TRAIN_ROWS]):
        block_y = train_start_y + index * (TRAIN_BLOCK_HEIGHT + TRAIN_BLOCK_GAP)
        _draw_train_section(
            draw,
            line_label,
            arrivals,
            data.timestamp,
            inner_left + 10,
            block_y,
            left_panel_width - 20,
            badge_font=medium_font,
            body_font=train_value_font,
            small_font=small_font,
        )

    # Right weather rail
    weather_left = right_panel_x + 10
    weather_top = header_bottom + 10
    draw.text((weather_left, weather_top), "Current Weather", font=small_font, fill=DISPLAY_FOREGROUND)
    _draw_weather_icon(draw, weather_left + 3, weather_top + 18, data.weather.condition)
    draw.text(
        (weather_left + 42, weather_top + 18),
        format_temperature(data.weather.temp),
        font=large_font,
        fill=DISPLAY_FOREGROUND,
    )
    draw.text(
        (weather_left + 42, weather_top + 49),
        data.weather.condition,
        font=small_font,
        fill=DISPLAY_FOREGROUND,
    )

    hourly_top = weather_top + 86
    draw.line((weather_left, hourly_top - 6, inner_right - 10, hourly_top - 6), fill=DISPLAY_FOREGROUND, width=1)
    _draw_hourly_list(
        draw,
        data.timestamp,
        data.weather.hourly,
        weather_left,
        hourly_top + 6,
        RIGHT_PANEL_WIDTH - 20,
        label_font=small_font,
        value_font=small_font,
    )

    # Small corner accents to echo the reference enclosure
    accent = 8
    draw.line((frame[0], frame[1] + accent, frame[0], frame[1]), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((frame[0], frame[1], frame[0] + accent, frame[1]), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((frame[2] - accent, frame[1], frame[2], frame[1]), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((frame[2], frame[1], frame[2], frame[1] + accent), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((frame[0], frame[3] - accent, frame[0], frame[3]), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((frame[0], frame[3], frame[0] + accent, frame[3]), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((frame[2] - accent, frame[3], frame[2], frame[3]), fill=DISPLAY_FOREGROUND, width=1)
    draw.line((frame[2], frame[3] - accent, frame[2], frame[3]), fill=DISPLAY_FOREGROUND, width=1)

    # Use imported constants to keep layout centralized for later iteration.
    _ = (
        DISPLAY_HEIGHT,
        DIVIDER_THICKNESS,
        SCREEN_PADDING,
        SECTION_GAP,
        TRAIN_ROW_HEIGHT,
        FORECAST_ITEM_WIDTH,
        FORECAST_ITEM_GAP,
    )

    return image
