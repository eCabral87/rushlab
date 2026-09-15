"""Demand-layer tests using committed fixtures; no network access."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from rushlab.config import Area, get_area
from rushlab.demand.bts import (
    PERSONAL_VEHICLES,
    latest_month,
    load_volumes,
    trailing_daily_average,
    volumes_from_rows,
)
from rushlab.demand.calibration import (
    calibrate,
    capacity_range,
    load_calibration,
    sink_overrides,
    write_calibration,
)
from rushlab.demand.cbp import append_snapshot, fetch_snapshot
from rushlab.demand.profile import (
    normalized_profile,
    peak_hour_demand,
    peak_share,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def area() -> Area:
    return get_area("san-ysidro")


@pytest.fixture()
def bts_frame(tmp_path: Path, area: Area) -> pd.DataFrame:
    rows = json.loads((FIXTURES / "bts_san_ysidro.json").read_text())
    cache_dir = tmp_path / "bts"
    cache_dir.mkdir()
    (cache_dir / f"{area.border.bts_port_code}.json").write_text(json.dumps(rows))
    return load_volumes(area, cache_root=cache_dir)


@pytest.fixture()
def snapshot(tmp_path: Path, area: Area) -> dict:
    payload = json.loads((FIXTURES / "bwt_san_ysidro.json").read_text())
    cache_dir = tmp_path / "cbp"
    cache_dir.mkdir()
    (cache_dir / f"{area.border.cbp_port_number}.json").write_text(json.dumps(payload))
    return fetch_snapshot(area, cache_root=cache_dir)


def test_profile_is_normalized() -> None:
    profile = normalized_profile()
    assert set(profile) == set(range(24))
    assert sum(profile.values()) == pytest.approx(1.0)


def test_peak_share_in_plausible_range() -> None:
    assert 0.25 <= peak_share() <= 0.45


def test_peak_hour_demand_uses_max_hour() -> None:
    profile = normalized_profile()
    expected = 100_000 * max(profile.values())
    assert peak_hour_demand(100_000) == pytest.approx(expected)


def test_bts_parsing_and_daily_average(bts_frame: pd.DataFrame) -> None:
    assert trailing_daily_average(bts_frame) == pytest.approx((1_200_000 / 30 + 1_337_174 / 31) / 2)
    assert latest_month(bts_frame) == "2026-07"


def test_bts_requires_expected_columns() -> None:
    with pytest.raises(ValueError, match="missing columns"):
        volumes_from_rows([{"date": "2026-01-01T00:00:00.000", "value": "1"}])


def test_cbp_normalization(snapshot: dict) -> None:
    assert snapshot["pov"]["max_lanes"] == 34
    assert snapshot["pov"]["general"]["delay_minutes"] == 170
    assert snapshot["pov"]["general"]["lanes_open"] == 4
    assert snapshot["pov"]["ready"]["delay_minutes"] == 150
    assert snapshot["pov"]["sentri"]["delay_minutes"] == 20
    assert snapshot["pedestrian"]["max_lanes"] == 22


def test_capacity_range_math() -> None:
    assert capacity_range(34) == {
        "low": pytest.approx(34 * 3600 / 60),
        "central": pytest.approx(34 * 3600 / 45),
        "high": pytest.approx(34 * 3600 / 30),
    }


def test_calibration_math_and_overrides(area: Area, snapshot: dict) -> None:
    calibration = calibrate(
        area_name=area.name,
        daily_average_veh=43_000.0,
        bts={"measure": PERSONAL_VEHICLES, "months": 12, "vintage": "2026-07"},
        snapshot=snapshot,
    )
    assert calibration["capacity_veh_h"]["central"] == pytest.approx(34 * 3600 / 45)
    assert calibration["peak_hour_demand_veh_h"] == pytest.approx(
        peak_hour_demand(43_000.0), abs=0.1
    )
    overrides = sink_overrides(calibration)
    assert overrides["sink_capacity_override"] == pytest.approx(34 * 3600 / 45)
    assert overrides["sink_delay_s"] == pytest.approx(170 * 60)


def test_calibration_roundtrip(tmp_path: Path, area: Area, snapshot: dict) -> None:
    calibration = calibrate(
        area_name=area.name,
        daily_average_veh=43_000.0,
        bts={"measure": PERSONAL_VEHICLES, "months": 12, "vintage": "2026-07"},
        snapshot=snapshot,
    )
    path = write_calibration(tmp_path / "calibration.json", calibration)
    assert load_calibration(path) == calibration
    assert load_calibration(tmp_path / "missing.json") is None


def test_snapshot_series_deduplicates(tmp_path: Path, snapshot: dict) -> None:
    path = tmp_path / "wait_snapshots.jsonl"
    assert append_snapshot(snapshot, path) is True
    assert append_snapshot(snapshot, path) is False
    assert len(path.read_text().splitlines()) == 1
