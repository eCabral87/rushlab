"""End-to-end baseline run on the fixture network (local SUMO, no network access)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rushlab.config import Area
from rushlab.demand.calibration import write_calibration
from rushlab.sim.runner import run_scenario


def test_baseline_end_to_end(mini_area: Area, mini_cache: Path, tmp_path: Path) -> None:
    derived = tmp_path / "derived"
    write_calibration(
        derived / mini_area.name / "calibration.json",
        {
            "area": mini_area.name,
            "volume": {"trailing_daily_average_veh": 800.0, "measure": "Personal Vehicles"},
            "capacity_veh_h": {"low": 200.0, "central": 400.0, "high": 600.0},
        },
    )
    summary = run_scenario(
        mini_area,
        window=(6, 7),
        seed=3,
        cache_root=mini_cache,
        derived_root=derived,
        results_root=tmp_path / "results",
    )
    metrics = summary["metrics"]
    assert summary["metering"] is not None
    assert summary["routed"]["routed"] == summary["plan"]["total_vehicles"]
    assert metrics["inserted"] > 0
    assert metrics["teleports"] == 0
    assert metrics.get("arrived", 0) > 0
    out = tmp_path / "results" / mini_area.name / "sumo" / "baseline" / "summary.json"
    assert json.loads(out.read_text())["metrics"] == metrics


def test_run_scenario_requires_calibration(mini_area: Area, tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="no calibration"):
        run_scenario(
            mini_area,
            cache_root=tmp_path / "cache",
            derived_root=tmp_path / "derived",
            results_root=tmp_path / "results",
        )
