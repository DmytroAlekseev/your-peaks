import json
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent

# All three data files, mapped to their mountain system name
DATA_FILES = {
    "Карпати":                   BASE_DIR / "carpathians_ua.json",
    "Кримські гори":             BASE_DIR / "crimea_mountains_ua.json",
    "Східноєвропейська рівнина": BASE_DIR / "east_european_plain_ua.json",
}

_mountains_cache: Optional[List[Dict]] = None


def load_mountains() -> List[Dict]:
    """Load and merge mountains from all three data files.
    Normalises field names so the rest of the app sees a consistent schema.
    Result is cached in memory after the first call.
    """
    global _mountains_cache
    if _mountains_cache is not None:
        return _mountains_cache

    mountains = []
    for system_name, path in DATA_FILES.items():
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for m in data["mountains"]:
            mountains.append({
                "id":               m["id"],
                "name":             m["name"],
                "elevation_m":      m["elevation_m"],
                "lat":              m["lat"],
                "lon":              m["lon"],
                "mountain_system":  system_name,
                # geo_oblast / geo_raion map to the existing "oblast" / "raion"
                # keys the API and frontend already understand
                "oblast":           m.get("geo_oblast", ""),
                "raion":            m.get("geo_raion", ""),
                "admin_oblast":     m.get("admin_oblast", ""),
                "admin_raion":      m.get("admin_raion", ""),
                "height_category":  m.get("height_category", ""),
                "climbed":          False,
                "climbed_at":       None,
            })

    _mountains_cache = mountains
    return mountains


def get_mountain_by_id(mountain_id: str) -> Optional[Dict]:
    return next((m for m in load_mountains() if m["id"] == mountain_id), None)


def filter_mountains(
    mountains: List[Dict],
    search: Optional[str] = None,
    mountain_system: Optional[str] = None,
    oblast: Optional[str] = None,
    raion: Optional[str] = None,
    min_elevation: Optional[int] = None,
    max_elevation: Optional[int] = None,
) -> List[Dict]:
    result = mountains

    if search:
        s = search.lower()
        result = [m for m in result if s in m["name"].lower()]

    if mountain_system:
        result = [m for m in result if m["mountain_system"] == mountain_system]

    if oblast:
        result = [m for m in result if m["oblast"] == oblast]

    if raion:
        result = [m for m in result if m["raion"] == raion]

    if min_elevation is not None:
        result = [m for m in result if m["elevation_m"] is not None and m["elevation_m"] >= min_elevation]

    if max_elevation is not None:
        result = [m for m in result if m["elevation_m"] is not None and m["elevation_m"] <= max_elevation]

    return result


def get_all_mountain_systems() -> List[str]:
    return list(DATA_FILES.keys())


def get_all_oblasts(mountain_system: Optional[str] = None) -> List[str]:
    mountains = load_mountains()
    if mountain_system:
        mountains = [m for m in mountains if m["mountain_system"] == mountain_system]
    return sorted(set(m["oblast"] for m in mountains if m["oblast"]))


def get_all_raions(oblast: Optional[str] = None) -> List[str]:
    mountains = load_mountains()
    if oblast:
        mountains = [m for m in mountains if m["oblast"] == oblast]
    return sorted(set(m["raion"] for m in mountains if m["raion"]))
