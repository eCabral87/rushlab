"""CLI smoke tests; no network access."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from rushlab import __version__
from rushlab.cli import app

runner = CliRunner()
FIXTURE = Path(__file__).parent / "fixtures" / "mini.graphml"


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_areas_lists_study_area() -> None:
    result = runner.invoke(app, ["areas"])
    assert result.exit_code == 0
    assert "san-ysidro" in result.stdout


def test_unknown_area_exits_with_error() -> None:
    result = runner.invoke(app, ["build-area", "nowhere"])
    assert result.exit_code == 2
    assert "unknown area" in result.stdout


def test_build_area_with_cached_fixture(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("rushlab.cli.fetch_area", lambda area, refresh=False: FIXTURE)
    monkeypatch.setattr("rushlab.cli.DERIVED_ROOT", tmp_path / "derived")
    result = runner.invoke(app, ["build-area", "san-ysidro"])
    assert result.exit_code == 0
    assert "border sink attached: yes" in result.stdout


def test_analyze_writes_report(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("rushlab.cli.fetch_area", lambda area, refresh=False: FIXTURE)
    monkeypatch.setattr("rushlab.cli.RESULTS_ROOT", tmp_path)
    monkeypatch.setattr("rushlab.cli.DERIVED_ROOT", tmp_path / "derived")
    result = runner.invoke(app, ["analyze", "san-ysidro", "--top", "3"])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "san-ysidro" / "analysis.json").is_file()


def test_demand_writes_calibration(monkeypatch, tmp_path: Path) -> None:
    import pandas as pd

    frame = pd.DataFrame(
        [
            {
                "measure": "Personal Vehicles",
                "value": 1200000,
                "date": pd.Timestamp("2026-06-01"),
            },
            {
                "measure": "Personal Vehicles",
                "value": 1337174,
                "date": pd.Timestamp("2026-07-01"),
            },
        ]
    )
    snapshot = {
        "pov": {
            "max_lanes": 34,
            "general": {"delay_minutes": 170, "lanes_open": 4},
            "ready": {"delay_minutes": 150, "lanes_open": 8},
            "sentri": {"delay_minutes": 20, "lanes_open": 15},
        },
        "date": "9/15/2026",
        "time": "13:00:00",
    }
    monkeypatch.setattr("rushlab.cli.load_volumes", lambda area, refresh=False: frame)
    monkeypatch.setattr("rushlab.cli.fetch_snapshot", lambda area, refresh=False: snapshot)
    monkeypatch.setattr("rushlab.cli.DERIVED_ROOT", tmp_path)
    result = runner.invoke(app, ["demand", "san-ysidro", "--no-snapshot"])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "san-ysidro" / "calibration.json").is_file()


def test_simulate_prints_kpis(monkeypatch) -> None:
    summary = {
        "area": "san-ysidro",
        "scenario": "baseline",
        "window": "06:00-10:00",
        "seed": 42,
        "plan": {"total_vehicles": 100},
        "metrics": {
            "inserted": 100,
            "arrived": 90,
            "teleports": 0,
            "mean_trip_duration_s": 120.0,
            "mean_trip_time_loss_s": 30.0,
            "max_port_queue_m": 50.0,
        },
        "metering": {
            "junction": "2",
            "cycle_s": 103.0,
            "port_green_s": 52.0,
            "port_green_ratio": 0.505,
            "estimated_capacity_veh_h": 2727.0,
        },
    }
    monkeypatch.setattr("rushlab.cli.run_scenario", lambda *args, **kwargs: summary)
    result = runner.invoke(app, ["simulate", "san-ysidro"])
    assert result.exit_code == 0, result.stdout
    assert "inserted" in result.stdout
    assert "port metering" in result.stdout


def test_simulate_rejects_bad_window() -> None:
    result = runner.invoke(app, ["simulate", "san-ysidro", "--window", "10:00-06:00"])
    assert result.exit_code == 2
    assert "window" in result.output
