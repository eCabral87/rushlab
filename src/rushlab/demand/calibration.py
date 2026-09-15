"""Demand-anchored border sink calibration with explicit ranges."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rushlab.demand.profile import (
    PEAK_WINDOW,
    PROFILE_NAME,
    PROFILE_SOURCE,
    peak_hour_demand,
    peak_share,
)

# Per-vehicle, per-lane primary inspection time (seconds). Central value 45 s
# is a mid-range assumption; the low/high bounds bracket it. Documented in ADR-0004.
DEFAULT_SERVICE_TIMES_S: dict[str, float] = {"low": 60.0, "central": 45.0, "high": 30.0}
METHOD = (
    "Demand-anchored estimate: BTS trailing daily volume x documented hourly profile "
    "-> peak-hour arrivals; capacity = max POV lanes x 3600/service_time with a "
    "service-time range. Not a fitted queueing model."
)


def capacity_range(
    max_lanes: int, service_times_s: dict[str, float] | None = None
) -> dict[str, float]:
    times = service_times_s or DEFAULT_SERVICE_TIMES_S
    return {level: max_lanes * 3600.0 / seconds for level, seconds in times.items()}


def calibrate(
    *,
    area_name: str,
    daily_average_veh: float,
    bts: dict[str, Any],
    snapshot: dict[str, Any],
    service_times_s: dict[str, float] | None = None,
) -> dict[str, Any]:
    peak_hour = peak_hour_demand(daily_average_veh)
    max_lanes = int(snapshot.get("pov", {}).get("max_lanes") or 0)
    capacity = capacity_range(max_lanes, service_times_s)
    utilisation = {level: peak_hour / value for level, value in capacity.items() if value}
    general = snapshot.get("pov", {}).get("general", {})
    observed_wait_min = general.get("delay_minutes")
    observed = {
        "general_wait_s": observed_wait_min * 60 if observed_wait_min else None,
        "general_lanes_open": general.get("lanes_open"),
        "snapshot_date": snapshot.get("date"),
        "snapshot_time": snapshot.get("time"),
    }
    return {
        "area": area_name,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "volume": {
            "measure": bts.get("measure", ""),
            "months": bts.get("months"),
            "bts_vintage": bts.get("vintage", ""),
            "trailing_daily_average_veh": round(daily_average_veh, 1),
        },
        "profile": {
            "name": PROFILE_NAME,
            "peak_window": f"{PEAK_WINDOW[0]:02d}:00-{PEAK_WINDOW[1]:02d}:00",
            "peak_window_share": round(peak_share(), 4),
            "source": PROFILE_SOURCE,
        },
        "peak_hour_demand_veh_h": round(peak_hour, 1),
        "lanes": {
            "max_pov": max_lanes,
            "snapshot_open": {
                lane: snapshot.get("pov", {}).get(lane, {}).get("lanes_open")
                for lane in ("general", "ready", "sentri")
            },
        },
        "service_time_seconds": service_times_s or DEFAULT_SERVICE_TIMES_S,
        "capacity_veh_h": {level: round(value, 1) for level, value in capacity.items()},
        "utilisation_vs_peak": {level: round(value, 2) for level, value in utilisation.items()},
        "observed": observed,
        "method": METHOD,
        "assumptions": [
            "BTS monthly volumes are inbound crossings; no outbound data exists.",
            "Hourly shape is the documented profile, not measured hourly demand.",
            "Max POV lanes are design capacity; snapshot open lanes reflect one moment.",
            "Service times bracket CBP primary inspection; not fitted to queue data.",
        ],
    }


def sink_overrides(calibration: dict[str, Any]) -> dict[str, float]:
    """Graph build overrides derived from a calibration result."""
    overrides: dict[str, float] = {}
    capacity = calibration.get("capacity_veh_h", {}).get("central")
    if capacity:
        overrides["sink_capacity_override"] = float(capacity)
    wait = calibration.get("observed", {}).get("general_wait_s")
    if wait:
        overrides["sink_delay_s"] = float(wait)
    return overrides


def write_calibration(path: Path, calibration: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(calibration, indent=2, ensure_ascii=False) + "\n")
    return path


def load_calibration(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text())
