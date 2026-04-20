"""Live MTA GTFS-Realtime transit data provider."""

from __future__ import annotations

import time
from typing import List

import requests
from google.transit import gtfs_realtime_pb2

try:
    from .config import MTA_API_KEY, MTA_FEED_URLS, SUBWAY_STOPS
    from .models import TrainArrival
except ImportError:
    from config import MTA_API_KEY, MTA_FEED_URLS, SUBWAY_STOPS
    from models import TrainArrival


def _fetch_feed(url: str) -> gtfs_realtime_pb2.FeedMessage | None:
    try:
        resp = requests.get(url, headers={"x-api-key": MTA_API_KEY}, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed


def get_train_data() -> List[TrainArrival]:
    now = time.time()
    arrivals: list[TrainArrival] = []

    for url in MTA_FEED_URLS:
        feed = _fetch_feed(url)
        if feed is None:
            continue

        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue
            tu = entity.trip_update
            route = tu.trip.route_id.upper()

            for stu in tu.stop_time_update:
                sid = stu.stop_id  # e.g. "F20N" or "F20S"

                for stop in SUBWAY_STOPS:
                    base = stop["stop_id"]
                    if not sid.startswith(base):
                        continue
                    if stop["lines"] and route not in stop["lines"]:
                        continue
                    direction = sid[len(base):]
                    if direction == "N":
                        destination = stop["north"]
                    elif direction == "S":
                        destination = stop["south"]
                    else:
                        continue

                    t = stu.arrival.time or stu.departure.time
                    if not t:
                        continue
                    minutes = round((t - now) / 60)
                    if minutes < 0:
                        continue

                    arrivals.append(TrainArrival(
                        line=route,
                        minutes=minutes,
                        destination=destination,
                    ))

    return sorted(arrivals, key=lambda a: (a.line, a.minutes))
