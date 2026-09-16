"""Self-contained HTML comparison report with embedded figures."""

from __future__ import annotations

import base64
import io
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from jinja2 import Template  # noqa: E402

TEMPLATE_PATH = Path(__file__).parent / "templates" / "scenario_report.html.j2"

BAR_KPIS: tuple[tuple[str, str], ...] = (
    ("mean_trip_time_loss_s", "Mean time loss (s)"),
    ("mean_trip_duration_s", "Mean trip duration (s)"),
    ("port_throughput_veh_h", "Port throughput (veh/h)"),
    ("teleports", "Teleports"),
)


def _figure_to_base64(figure: Any) -> str:
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", dpi=110, bbox_inches="tight")
    plt.close(figure)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def build_kpi_figure(comparison: dict[str, Any]) -> str | None:
    scenarios = comparison["scenarios"]
    rows_by_key = {row["key"]: row for row in comparison["rows"]}
    available = [
        (label, rows_by_key[key])
        for key, label in BAR_KPIS
        if key in rows_by_key
        and any(rows_by_key[key]["values"][name] is not None for name in scenarios)
    ]
    if not available:
        return None
    figure, axes = plt.subplots(1, len(available), figsize=(3.4 * len(available), 3.0))
    if len(available) == 1:
        axes = [axes]
    colors = ["#718096", "#2b6cb0", "#2f855a", "#b7791f"]
    for axis, (label, row) in zip(axes, available, strict=True):
        values = [row["values"][name] or 0.0 for name in scenarios]
        axis.bar(scenarios, values, color=colors[: len(scenarios)])
        axis.set_title(label, fontsize=9)
        axis.tick_params(axis="x", labelrotation=15)
    figure.suptitle("Scenario KPIs", fontsize=11)
    return _figure_to_base64(figure)


def build_port_throughput_figure(results_root: Path, area: str, scenarios: list[str]) -> str | None:
    import json

    figure, axis = plt.subplots(figsize=(7.0, 3.0))
    plotted = False
    for index, scenario in enumerate(scenarios):
        summary_path = results_root / area / "sumo" / scenario / "summary.json"
        edgedata_path = results_root / area / "sumo" / scenario / "edgedata.xml"
        if not summary_path.is_file() or not edgedata_path.is_file():
            continue
        destination = json.loads(summary_path.read_text()).get("destination_edge")
        if not destination:
            continue
        intervals: list[tuple[float, float]] = []
        for interval in ET.parse(edgedata_path).getroot().findall("interval"):
            begin = float(interval.get("begin", 0))
            end = float(interval.get("end", 0))
            arrived = sum(
                float(edge.get("arrived", 0))
                for edge in interval.findall("edge")
                if edge.get("id") == destination
            )
            if end > begin:
                intervals.append((begin / 3600.0, arrived * 3600.0 / (end - begin)))
        if intervals:
            axis.plot(
                [hour for hour, _ in intervals],
                [value for _, value in intervals],
                label=scenario,
                color=["#718096", "#2b6cb0", "#2f855a"][index % 3],
            )
            plotted = True
    if not plotted:
        plt.close(figure)
        return None
    axis.set_xlabel("hour")
    axis.set_ylabel("port arrivals (veh/h)")
    axis.set_title("Port throughput over time")
    axis.legend()
    return _figure_to_base64(figure)


def build_trip_duration_figure(results_root: Path, area: str, scenarios: list[str]) -> str | None:
    figure, axis = plt.subplots(figsize=(7.0, 3.0))
    plotted = False
    for index, scenario in enumerate(scenarios):
        path = results_root / area / "sumo" / scenario / "tripinfo.xml"
        if not path.is_file():
            continue
        durations = [
            float(trip.get("duration", 0)) / 60.0
            for trip in ET.parse(path).getroot().findall("tripinfo")
        ]
        if durations:
            axis.hist(
                durations,
                bins=40,
                alpha=0.5,
                label=scenario,
                color=["#718096", "#2b6cb0", "#2f855a"][index % 3],
            )
            plotted = True
    if not plotted:
        plt.close(figure)
        return None
    axis.set_xlabel("trip duration (minutes)")
    axis.set_ylabel("vehicles")
    axis.set_title("Trip duration distribution")
    axis.legend()
    return _figure_to_base64(figure)


def render_report(output_path: Path, comparison: dict[str, Any], figures: dict[str, str]) -> Path:
    template = Template(TEMPLATE_PATH.read_text())
    html = template.render(comparison=comparison, figures=figures)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    return output_path
