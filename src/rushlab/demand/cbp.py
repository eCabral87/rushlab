"""CBP Border Wait Times live client and snapshot series."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from rushlab.config import Area

BWT_URL = "https://bwt.cbp.gov/api/bwtnew"
DEFAULT_CACHE_ROOT = Path("data/cache/cbp")


def _to_int(value: object) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _clean_lane(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "update_time": str(raw.get("update_time", "")),
        "status": str(raw.get("operational_status", "")),
        "delay_minutes": _to_int(raw.get("delay_minutes")),
        "lanes_open": _to_int(raw.get("lanes_open")),
    }


def normalize_port(entry: dict[str, Any]) -> dict[str, Any]:
    passenger = entry.get("passenger_vehicle_lanes") or {}
    pedestrian = entry.get("pedestrian_lanes") or {}
    return {
        "port_number": str(entry.get("port_number", "")),
        "port_name": str(entry.get("port_name", "")),
        "date": str(entry.get("date", "")),
        "time": str(entry.get("time", "")),
        "status": str(entry.get("port_status", "")),
        "pov": {
            "max_lanes": _to_int(passenger.get("maximum_lanes")),
            "general": _clean_lane(passenger.get("standard_lanes") or {}),
            "ready": _clean_lane(passenger.get("ready_lanes") or {}),
            "sentri": _clean_lane(passenger.get("NEXUS_SENTRI_lanes") or {}),
        },
        "pedestrian": {
            "max_lanes": _to_int(pedestrian.get("maximum_lanes")),
            "general": _clean_lane(pedestrian.get("standard_lanes") or {}),
            "ready": _clean_lane(pedestrian.get("ready_lanes") or {}),
        },
    }


def fetch_snapshot(
    area: Area, *, refresh: bool = False, cache_root: Path = DEFAULT_CACHE_ROOT
) -> dict[str, Any]:
    """Return a normalized CBP wait-time snapshot for the area's port."""
    if area.border is None or not area.border.cbp_port_number:
        raise ValueError("area has no CBP port number; add border.cbp_port_number")
    port = area.border.cbp_port_number
    cache = cache_root / f"{port}.json"
    if cache.is_file() and not refresh:
        payload = json.loads(cache.read_text())
    else:
        response = httpx.get(BWT_URL, timeout=60.0, follow_redirects=True)
        response.raise_for_status()
        payload = response.json()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(payload, ensure_ascii=False))

    entry = next((row for row in payload if str(row.get("port_number")) == port), None)
    if entry is None:
        raise ValueError(f"port {port} not found in CBP BWT feed")
    snapshot = normalize_port(entry)
    snapshot["fetched_at"] = datetime.now(UTC).isoformat(timespec="seconds")
    return snapshot


def append_snapshot(snapshot: dict[str, Any], path: Path) -> bool:
    """Append the snapshot to a JSONL series; duplicates (same date/time) are skipped."""
    path.parent.mkdir(parents=True, exist_ok=True)
    key = (snapshot.get("date"), snapshot.get("time"))
    if path.is_file():
        for line in path.read_text().splitlines():
            record = json.loads(line)
            if (record.get("date"), record.get("time")) == key:
                return False
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
    return True
