"""Report comparison and rendering tests."""

from __future__ import annotations

from pathlib import Path

from rushlab.report.compare import build_comparison
from rushlab.report.html import build_kpi_figure, render_report


def fake_summary(
    *, time_loss: float, throughput: float, teleports: int, arrived: int, algorithm: str | None
) -> dict:
    return {
        "area": "mini",
        "scenario": "s",
        "window": "06:00-10:00",
        "seed": 42,
        "plan": {"total_vehicles": 100, "demand_factor": 0.75},
        "metering": {"junction": "2"},
        "signals": (
            {"algorithm": algorithm, "junctions": ["a", "b"], "cycle_s": 90.0}
            if algorithm
            else None
        ),
        "metrics": {
            "mean_trip_time_loss_s": time_loss,
            "mean_trip_duration_s": time_loss + 100,
            "port_throughput_veh_h": throughput,
            "port_throughput_peak_veh_h": throughput + 100,
            "port_approach_waiting_time_s": time_loss * 2,
            "teleports": teleports,
            "arrived": arrived,
            "inserted": arrived + 1,
        },
    }


def test_build_comparison_deltas() -> None:
    summaries = {
        "baseline": fake_summary(
            time_loss=100.0, throughput=1000.0, teleports=10, arrived=90, algorithm=None
        ),
        "optimized": fake_summary(
            time_loss=80.0, throughput=1100.0, teleports=5, arrived=95, algorithm="webster+ga"
        ),
    }
    comparison = build_comparison("mini", summaries)
    rows = {row["key"]: row for row in comparison["rows"]}
    assert rows["mean_trip_time_loss_s"]["delta_pct"]["optimized"] == -20.0
    assert rows["port_throughput_veh_h"]["delta_pct"]["optimized"] == 10.0
    assert comparison["provenance"]["optimized"]["signals"]["algorithm"] == "webster+ga"


def test_render_report_writes_html(tmp_path: Path) -> None:
    summaries = {
        "baseline": fake_summary(
            time_loss=100.0, throughput=1000.0, teleports=10, arrived=90, algorithm=None
        ),
        "optimized": fake_summary(
            time_loss=80.0, throughput=1100.0, teleports=5, arrived=95, algorithm="webster+ga"
        ),
    }
    comparison = build_comparison("mini", summaries)
    figure = build_kpi_figure(comparison)
    out = render_report(tmp_path / "report.html", comparison, {"kpis": figure or ""})
    html = out.read_text()
    assert "Assumptions and provenance" in html
    assert "baseline" in html and "optimized" in html
    assert "-20.0%" in html


def test_render_report_without_figures(tmp_path: Path) -> None:
    comparison = build_comparison(
        "mini",
        {
            "baseline": fake_summary(
                time_loss=1.0, throughput=1.0, teleports=0, arrived=1, algorithm=None
            )
        },
    )
    out = render_report(tmp_path / "plain.html", comparison, {})
    assert out.is_file()
