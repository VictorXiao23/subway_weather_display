"""UI rendering for the e-paper display."""

from __future__ import annotations

import math
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

try:
    from .config import (
        DISPLAY_BACKGROUND,
        DISPLAY_FOREGROUND,
        DISPLAY_HEIGHT,
        DISPLAY_WIDTH,
        FONT_LARGE_SIZE,
        FONT_MEDIUM_SIZE,
        FONT_SMALL_SIZE,
        MAX_FORECAST_HOURS,
        MAX_TRAIN_ROWS,
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
        FONT_LARGE_SIZE,
        FONT_MEDIUM_SIZE,
        FONT_SMALL_SIZE,
        MAX_FORECAST_HOURS,
        MAX_TRAIN_ROWS,
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
HEADER_HEIGHT = 58
RIGHT_PANEL_WIDTH = 270
LEFT_PANEL_MIN_WIDTH = 0
ROUTE_BADGE_SIZE = 58
TRAIN_BLOCK_HEIGHT = 87
TRAIN_BLOCK_GAP = 6
WEATHER_ICON_SIZE = 56
HOURLY_ROW_HEIGHT = 34
TRAIN_ROW_SPACING = 28
TRAIN_VALUE_FONT_SIZE = 24
WEATHER_VALUE_FONT_SIZE = 48
WEATHER_DETAIL_FONT_SIZE = 24
HEADER_VALUE_FONT_SIZE = 34
HEADER_META_FONT_SIZE = 30
TRAIN_DIRECTION_GAP = 18


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


def _draw_cloud(draw: ImageDraw.ImageDraw, x: int, y: int, s: float) -> None:
    w = max(1, round(s))
    bumps = [
        (round(x + 4*s),  round(y + 17*s), round(4*s)),
        (round(x + 10*s), round(y + 14*s), round(7*s)),
        (round(x + 17*s), round(y + 11*s), round(9*s)),
        (round(x + 24*s), round(y + 14*s), round(7*s)),
        (round(x + 29*s), round(y + 17*s), round(4*s)),
    ]
    for cx, cy, r in bumps:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=DISPLAY_FOREGROUND)
    for cx, cy, r in bumps:
        ri = r - w
        if ri > 0:
            draw.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), fill=DISPLAY_BACKGROUND)


def _draw_sun(draw: ImageDraw.ImageDraw, cx: int, cy: int, s: float) -> None:
    r = round(8*s)
    w = max(1, round(s))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=DISPLAY_FOREGROUND, width=w)
    for deg in range(0, 360, 45):
        angle = math.radians(deg)
        x1 = cx + round((r + round(2*s)) * math.cos(angle))
        y1 = cy + round((r + round(2*s)) * math.sin(angle))
        x2 = cx + round((r + round(5*s)) * math.cos(angle))
        y2 = cy + round((r + round(5*s)) * math.sin(angle))
        draw.line((x1, y1, x2, y2), fill=DISPLAY_FOREGROUND, width=w)


def _draw_weather_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, condition: str) -> None:
    s = size / 30
    n = condition.lower()
    cx, cy = x + round(16*s), y + round(16*s)
    w = max(1, round(s))

    if "sun" in n or "clear" in n:
        _draw_sun(draw, cx, cy, s)
    elif "storm" in n or "thunder" in n:
        _draw_cloud(draw, x, y, s)
        pts = [
            (cx,              y + round(14*s)),
            (cx - round(4*s), y + round(22*s)),
            (cx + round(2*s), y + round(22*s)),
            (cx - round(2*s), y + round(30*s)),
            (cx + round(6*s), y + round(20*s)),
            (cx + round(2*s), y + round(20*s)),
            (cx + round(4*s), y + round(14*s)),
        ]
        draw.polygon(pts, fill=DISPLAY_FOREGROUND)
    elif "rain" in n or "shower" in n:
        _draw_cloud(draw, x, y, s)
        for i in range(3):
            rx = x + round((10 + i * 7) * s)
            draw.line((rx, y + round(27*s), rx - round(3*s), y + round(33*s)), fill=DISPLAY_FOREGROUND, width=w)
    elif "snow" in n or "sleet" in n or "hail" in n:
        r = round(12*s)
        for deg in [0, 60, 120]:
            angle = math.radians(deg)
            draw.line((cx - round(r*math.cos(angle)), cy - round(r*math.sin(angle)),
                       cx + round(r*math.cos(angle)), cy + round(r*math.sin(angle))),
                      fill=DISPLAY_FOREGROUND, width=w)
    elif "fog" in n or "mist" in n or "haze" in n:
        cloud_scale = 0.65
        cloud_w = round(33 * cloud_scale * s)
        cloud_x = x + (round(30*s) - cloud_w) // 2
        cloud_y = y + round(2*s)
        _draw_cloud(draw, cloud_x, cloud_y, s * cloud_scale)
        line_cx = x + round(15*s)
        line_y = cloud_y + round(21 * cloud_scale * s) + round(3*s)
        for i, half_w in enumerate([12, 10, 8]):
            lx = line_cx - round(half_w * s)
            rx = line_cx + round(half_w * s)
            draw.line((lx, line_y + i * round(4*s), rx, line_y + i * round(4*s)),
                      fill=DISPLAY_FOREGROUND, width=w)
    elif "part" in n:
        _draw_sun(draw, x + round(20*s), y + round(10*s), s * 0.7)
        _draw_cloud(draw, x, y + round(8*s), s * 0.8)
    else:
        _draw_cloud(draw, x, y, s)


def _group_trains_by_line(trains) -> list[tuple[str, Sequence]]:
    grouped: dict[str, list] = {}
    for train in trains:
        grouped.setdefault(train.line, []).append(train)
    return list(grouped.items())


def _group_arrivals_by_destination(arrivals: Sequence) -> list[tuple[str, Sequence]]:
    grouped: dict[str, list] = {}
    for arrival in arrivals:
        grouped.setdefault(arrival.destination, []).append(arrival)
    # N/E before S/W
    order = {"N": 0, "E": 0, "S": 1, "W": 1}
    return sorted(grouped.items(), key=lambda item: order.get(item[1][0].direction, 2))


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
    direction_font: ImageFont.ImageFont,
) -> None:
    """Draw one grouped train block with both travel directions."""

    badge_center_x = x + (ROUTE_BADGE_SIZE // 2)
    badge_center_y = y + 43
    _draw_route_badge(draw, badge_center_x, badge_center_y, line_label, badge_font)

    content_x = x + ROUTE_BADGE_SIZE + 24
    content_width = width - (content_x - x)
    direction_groups = _group_arrivals_by_destination(arrivals)[:2]
    direction_width = (content_width - TRAIN_DIRECTION_GAP) // 2

    for column_index, (destination, direction_arrivals) in enumerate(direction_groups):
        column_x = content_x + column_index * (direction_width + TRAIN_DIRECTION_GAP)
        draw.text((column_x, y + 2), destination, font=direction_font, fill=DISPLAY_FOREGROUND)

        for row_index, train in enumerate(direction_arrivals[:2]):
            row_y = y + 28 + (row_index * TRAIN_ROW_SPACING)
            minutes_value = "0" if train.minutes <= 0 else str(train.minutes)
            minutes_width, _ = _measure_text(draw, minutes_value, body_font)
            minutes_x = column_x
            min_label_x = minutes_x + minutes_width + 4
            arrival_text = format_arrival_clock(timestamp, train.minutes)
            time_width, _ = _measure_text(draw, arrival_text, body_font)
            time_x = column_x + direction_width - time_width

            draw.text((minutes_x, row_y), minutes_value, font=body_font, fill=DISPLAY_FOREGROUND)
            draw.text((min_label_x, row_y + 5), "min", font=small_font, fill=DISPLAY_FOREGROUND)
            draw.text((time_x, row_y), arrival_text, font=body_font, fill=DISPLAY_FOREGROUND)

    draw.line((content_x, y + TRAIN_BLOCK_HEIGHT - 4, x + width, y + TRAIN_BLOCK_HEIGHT - 4), fill=DISPLAY_FOREGROUND, width=1)


def _draw_hourly_list(
    draw: ImageDraw.ImageDraw,
    timestamp,
    temperatures: Sequence[int],
    condition: str,
    x: int,
    y: int,
    width: int,
    label_font: ImageFont.ImageFont,
    value_font: ImageFont.ImageFont,
) -> None:
    icon_size = HOURLY_ROW_HEIGHT - 4
    icon_v_offset = (HOURLY_ROW_HEIGHT - icon_size) // 2
    label_w, _ = _measure_text(draw, "12 pm", label_font)
    temp_sample_w, _ = _measure_text(draw, "100°", value_font)
    label_end = x + label_w + 6
    temp_start = x + width - temp_sample_w
    icon_x = label_end + (temp_start - label_end - icon_size) // 2

    for index, temp in enumerate(temperatures[:MAX_FORECAST_HOURS]):
        row_y = y + (index * HOURLY_ROW_HEIGHT)
        hour_label = format_forecast_hour(timestamp, index + 1)
        temp_label = format_temperature(temp)
        draw.text((x, row_y), hour_label, font=label_font, fill=DISPLAY_FOREGROUND)
        _draw_weather_icon(draw, icon_x, row_y + icon_v_offset, icon_size, condition)
        temp_width, _ = _measure_text(draw, temp_label, value_font)
        draw.text((x + width - temp_width, row_y), temp_label, font=value_font, fill=DISPLAY_FOREGROUND)


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Load a clean sans-serif font with a safe fallback."""

    if bold:
        preferred_fonts = (
            "DejaVuSans-Bold.ttf",
            "Arial Bold.ttf",
            "LiberationSans-Bold.ttf",
            "DejaVuSans.ttf",
        )
    else:
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
    badge_font = _load_font(30, bold=True)
    small_font = _load_font(FONT_SMALL_SIZE)
    train_value_font = _load_font(TRAIN_VALUE_FONT_SIZE)
    weather_value_font = _load_font(WEATHER_VALUE_FONT_SIZE)
    weather_detail_font = _load_font(WEATHER_DETAIL_FONT_SIZE)
    forecast_label_font = _load_font(21)
    forecast_temp_font = _load_font(23)
    direction_font = _load_font(FONT_SMALL_SIZE, bold=True)
    header_value_font = _load_font(HEADER_VALUE_FONT_SIZE, bold=True)
    header_meta_font = _load_font(HEADER_META_FONT_SIZE, bold=True)

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
    date_width, _ = _measure_text(draw, date_text, header_meta_font)
    draw.text((inner_left + 18, inner_top + 10), date_text, font=header_meta_font, fill=DISPLAY_FOREGROUND)
    divider_x = inner_left + 18 + date_width + 18
    draw.line((divider_x, inner_top + 10, divider_x, header_bottom - 11), fill=DISPLAY_FOREGROUND, width=1)
    draw.text((divider_x + 18, inner_top + 8), time_text, font=header_value_font, fill=DISPLAY_FOREGROUND)

    # Left transit panel — distribute blocks evenly across available height
    grouped_trains = _group_trains_by_line(data.trains)
    num_blocks = min(len(grouped_trains), MAX_TRAIN_ROWS)
    available_train_height = inner_bottom - header_bottom
    even_gap = (available_train_height - num_blocks * TRAIN_BLOCK_HEIGHT) // (num_blocks + 1)
    train_start_y = header_bottom + even_gap
    for index, (line_label, arrivals) in enumerate(grouped_trains[:MAX_TRAIN_ROWS]):
        block_y = train_start_y + index * (TRAIN_BLOCK_HEIGHT + even_gap)
        _draw_train_section(
            draw,
            line_label,
            arrivals,
            data.timestamp,
            inner_left + 18,
            block_y,
            left_panel_width - 36,
            badge_font=badge_font,
            body_font=train_value_font,
            small_font=small_font,
            direction_font=direction_font,
        )

    # Right weather rail
    weather_left = right_panel_x + 18
    weather_top = header_bottom + 14
    _draw_weather_icon(draw, weather_left + 6, weather_top, WEATHER_ICON_SIZE, data.weather.condition)
    draw.text(
        (weather_left + 86, weather_top),
        format_temperature(data.weather.temp),
        font=weather_value_font,
        fill=DISPLAY_FOREGROUND,
    )
    draw.text(
        (weather_left + 86, weather_top + 50),
        data.weather.condition,
        font=weather_detail_font,
        fill=DISPLAY_FOREGROUND,
    )

    hourly_top = weather_top + 100
    draw.line((weather_left, hourly_top - 10, inner_right - 18, hourly_top - 10), fill=DISPLAY_FOREGROUND, width=1)
    _draw_hourly_list(
        draw,
        data.timestamp,
        data.weather.hourly,
        data.weather.condition,
        weather_left,
        hourly_top + 6,
        RIGHT_PANEL_WIDTH - 36,
        label_font=forecast_label_font,
        value_font=forecast_temp_font,
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

    return image
