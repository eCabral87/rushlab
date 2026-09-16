"""Scenario comparison tables."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

KPI_ROWS: tuple[tuple[str, str, str], ...] = (
    ("mean_trip_time_loss_s", "Mean time loss (s)", "lower"),
    ("mean_trip_duration_s", "Mean trip duration (s)", "lower"),
    ("port_throughput_veh_h", "Port throughput (veh/h)", "higher"),
    ("port_throughput_peak_veh_h", "Port throughput peak (veh/h)", "higher"),
    ("port_approach_waiting_time_s", "Port approach waiting (s)", "lower"),
    ("teleports", "Teleports", "lower"),
    ("arrived", "Arrived vehicles", "higher"),
    ("inserted", "Inserted vehicles", "higher"),
)


def load_scenario_summary(results_root: Path, area: str, scenario: str) -> dict[str, Any]:
    path = results_root / area / "sumo" / scenario / "summary.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"no summary for scenario {scenario!r}; "
            f"run: rushlab simulate {area} --scenario {scenario}"
        )
    return json.loads(path.read_text())


def build_comparison(area: str, summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Ranked KPI table with percent deltas against the first scenario (baseline)."""
    scenario_names = list(summaries)
    if not scenario_names:
        raise ValueError("no scenarios to compare")
    baseline_name = scenario_names[0]

    rows: list[dict[str, Any]] = []
    for key, label, direction in KPI_ROWS:
        values = {name: summary["metrics"].get(key) for name, summary in summaries.items()}
        baseline_value = values.get(baseline_name)
        delta_pct: dict[str, float | None] = {}
        for name, value in values.items():
            if value is None or not baseline_value:
                delta_pct[name] = None
            else:
                delta_pct[name] = round(100.0 * (value - baseline_value) / baseline_value, 1)
        rows.append(
            {
                "key": key,
                "label": label,
                "direction": direction,
                "values": values,
                "delta_pct": delta_pct,
            }
        )

    provenance = {
        name: {
            "window": summary.get("window"),
            "seed": summary.get("seed"),
            "metering": bool(summary.get("metering")),
            "signals": summary.get("signals"),
            "plan_vehicles": (summary.get("plan") or {}).get("total_vehicles"),
            "demand_factor": (summary.get("plan") or {}).get("demand_factor"),
        }
        for name, summary in summaries.items()
    }
    return {
        "area": area,
        "baseline": baseline_name,
        "scenarios": scenario_names,
        "rows": rows,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "provenance": provenance,
    }
