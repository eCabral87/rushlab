"""BTS Border Crossing/Entry Data client (Socrata)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

from rushlab.config import Area

BTS_RESOURCE = "https://data.transportation.gov/resource/keg4-3bc2.json"
DEFAULT_CACHE_ROOT = Path("data/cache/bts")
PERSONAL_VEHICLES = "Personal Vehicles"
PEDESTRIANS = "Pedestrians"


def volumes_from_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    missing = {"measure", "value", "date"} - set(frame.columns)
    if missing:
        raise ValueError(f"BTS rows missing columns: {sorted(missing)}")
    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame["value"] = frame["value"].astype(int)
    return frame.sort_values(by="date").reset_index(drop=True)


def fetch_volumes(
    area: Area,
    *,
    months: int = 12,
    refresh: bool = False,
    cache_root: Path = DEFAULT_CACHE_ROOT,
) -> Path:
    """Return the cached raw BTS payload path, downloading when needed."""
    if area.border is None or not area.border.bts_port_code:
        raise ValueError("area has no BTS port code; add border.bts_port_code")
    cache = cache_root / f"{area.border.bts_port_code}.json"
    if cache.is_file() and not refresh:
        return cache
    params = {
        "$where": f"port_code='{area.border.bts_port_code}'",
        "$order": "date DESC",
        "$limit": str(months * 10),
    }
    response = httpx.get(BTS_RESOURCE, params=params, timeout=60.0, follow_redirects=True)
    response.raise_for_status()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(response.json(), indent=2, ensure_ascii=False) + "\n")
    return cache


def load_volumes(
    area: Area,
    *,
    months: int = 12,
    refresh: bool = False,
    cache_root: Path = DEFAULT_CACHE_ROOT,
) -> pd.DataFrame:
    path = fetch_volumes(area, months=months, refresh=refresh, cache_root=cache_root)
    return volumes_from_rows(json.loads(path.read_text()))


def trailing_daily_average(
    frame: pd.DataFrame, measure: str = PERSONAL_VEHICLES, *, months: int = 12
) -> float:
    subset: pd.DataFrame = frame.loc[frame["measure"] == measure].tail(months)
    if subset.empty:
        raise ValueError(f"no BTS rows for measure {measure!r}")
    daily = subset["value"] / subset["date"].dt.days_in_month
    return float(daily.mean())


def latest_month(frame: pd.DataFrame, measure: str = PERSONAL_VEHICLES) -> str:
    subset = frame[frame["measure"] == measure]
    if subset.empty:
        raise ValueError(f"no BTS rows for measure {measure!r}")
    return str(subset["date"].max().strftime("%Y-%m"))
