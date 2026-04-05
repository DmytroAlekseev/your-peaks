import json
from pathlib import Path
from typing import List, Dict, Optional

DATA_PATH = Path(__file__).parent / "carpathian_ua.json"

_mountains_cache: Optional[List[Dict]] = None


def load_mountains() -> List[Dict]:
    """Load all mountains from JSON, flattening group hierarchy into a list.
    Result is cached in memory after the first call.
    """
    global _mountains_cache
    if _mountains_cache is not None:
        return _mountains_cache

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    mountains = []
    for group in data["groups"]:
        for m in group["mountains"]:
            mountains.append({
                "id": m["id"],
                "name": m["name"],
                "elevation_m": m["elevation_m"],
                "lat": m["lat"],
                "lon": m["lon"],
                "oblast": group["oblast"],
                "raion": group["raion"],
                "climbed": False,
                "climbed_at": None,
            })

    _mountains_cache = mountains
    return mountains


def get_mountain_by_id(mountain_id: str) -> Optional[Dict]:
    return next((m for m in load_mountains() if m["id"] == mountain_id), None)


def filter_mountains(
    mountains: List[Dict],
    search: Optional[str] = None,
    oblast: Optional[str] = None,
    raion: Optional[str] = None,
    min_elevation: Optional[int] = None,
    max_elevation: Optional[int] = None,
) -> List[Dict]:
    result = mountains

    if search:
        s = search.lower()
        result = [m for m in result if s in m["name"].lower()]

    if oblast:
        result = [m for m in result if m["oblast"] == oblast]

    if raion:
        result = [m for m in result if m["raion"] == raion]

    if min_elevation is not None:
        result = [m for m in result if m["elevation_m"] >= min_elevation]

    if max_elevation is not None:
        result = [m for m in result if m["elevation_m"] <= max_elevation]

    return result


def get_all_oblasts() -> List[str]:
    return sorted(set(m["oblast"] for m in load_mountains()))


def get_all_raions() -> List[str]:
    return sorted(set(m["raion"] for m in load_mountains()))
