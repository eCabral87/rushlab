"""RushLab MCP server exposing domain tools over stdio (MCP 2.x)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from rushlab import __version__
from rushlab.config import Area, get_area, load_areas
from rushlab.demand.calibration import load_calibration, sink_overrides
from rushlab.network.build import build_analysis_graph
from rushlab.network.fetch import area_cache_dir
from rushlab.network.metrics import analyze_area
from rushlab.report.compare import build_comparison, load_scenario_summary
from rushlab.report.html import (
    build_kpi_figure,
    build_port_throughput_figure,
    build_trip_duration_figure,
)
from rushlab.report.html import (
    render_report as render_html_report,
)
from rushlab.signals.study import optimize_area_signals
from rushlab.sim.runner import run_scenario

REPO_ROOT = Path(__file__).resolve().parents[2]
DERIVED_ROOT = REPO_ROOT / "data" / "derived"
RESULTS_ROOT = REPO_ROOT / "results"
OSM_CACHE_ROOT = REPO_ROOT / "data" / "cache" / "areas"
REPORTS_ROOT = REPO_ROOT / "docs" / "reports"

server = MCPServer(
    name="rushlab",
    title="RushLab traffic scenario lab",
    version=__version__,
    instructions=(
        "RushLab analyzes and simulates the San Ysidro border approach in Tijuana. "
        "Read-only tools: list_areas, area_analysis, area_calibration, scenario_metrics, "
        "compare_scenarios. Action tools: run_simulation (minutes), optimize_signals "
        "(tens of minutes; requires confirm=true), render_report (seconds). "
        "All results are relative comparisons under documented assumptions, not predictions."
    ),
)


def _area_or_error(name: str) -> Area:
    try:
        return get_area(name)
    except KeyError as exc:
        raise ValueError(str(exc.args[0])) from None


def _parse_window(value: str) -> tuple[int, int]:
    try:
        start_text, end_text = value.split("-", 1)
        start = int(start_text.split(":", 1)[0])
        end = int(end_text.split(":", 1)[0])
    except (ValueError, IndexError):
        raise ValueError("window must look like 06:00-10:00") from None
    if not 0 <= start < end <= 24:
        raise ValueError("window hours must satisfy 0 <= start < end <= 24")
    return start, end


def _safe_output_path(relative: str) -> Path:
    candidate = (REPO_ROOT / relative).resolve()
    allowed = tuple(root.resolve() for root in (RESULTS_ROOT, REPORTS_ROOT))
    if candidate.suffix != ".html":
        raise ValueError("report output must end with .html")
    if not any(candidate.is_relative_to(root) for root in allowed):
        allowed_names = [str(root.relative_to(REPO_ROOT)) for root in allowed]
        raise ValueError(f"output must stay under {allowed_names}")
    return candidate


def _safe_repo_path(relative: str) -> Path:
    candidate = (REPO_ROOT / relative).resolve()
    if not candidate.is_relative_to(REPO_ROOT):
        raise ValueError("path must stay inside the repository")
    return candidate


def list_areas() -> list[dict[str, Any]]:
    """Registered study areas with bounding boxes and descriptions."""
    return [
        {
            "name": area.name,
            "description": area.description,
            "bbox": list(area.bbox),
            "sim_bbox": list(area.sim_bbox) if area.sim_bbox else None,
        }
        for area in load_areas().values()
    ]


def area_analysis(area: str, top: int = 10) -> dict[str, Any]:
    """Bottlenecks, connectivity, and min-cut analysis from the cached OSM graph."""
    if top < 1:
        raise ValueError("top must be >= 1")
    config = _area_or_error(area)
    graphml = area_cache_dir(config.name, OSM_CACHE_ROOT) / "graph.graphml"
    if not graphml.is_file():
        raise RuntimeError(f"no cached OSM graph for {area}; run: rushlab fetch-area {area}")
    calibration = load_calibration(DERIVED_ROOT / config.name / "calibration.json")
    overrides = sink_overrides(calibration) if calibration else {}
    graph = build_analysis_graph(graphml, area=config, **overrides)
    report = analyze_area(graph, config, top=top)
    report["calibration"] = "derived" if overrides else "placeholder"
    return report


def area_calibration(area: str) -> dict[str, Any]:
    """Derived demand calibration (volume, capacity range, provenance) for an area."""
    config = _area_or_error(area)
    calibration = load_calibration(DERIVED_ROOT / config.name / "calibration.json")
    if calibration is None:
        raise RuntimeError(f"no calibration for {area}; run: rushlab demand {area}")
    return calibration


def scenario_metrics(area: str, scenario: str = "baseline") -> dict[str, Any]:
    """KPI metrics for one simulation scenario summary."""
    config = _area_or_error(area)
    summary = load_scenario_summary(RESULTS_ROOT, config.name, scenario)
    return {
        "area": config.name,
        "scenario": scenario,
        "window": summary.get("window"),
        "seed": summary.get("seed"),
        "signals": summary.get("signals"),
        "metering": summary.get("metering"),
        "metrics": summary.get("metrics", {}),
    }


def compare_scenarios(area: str, scenarios: list[str]) -> dict[str, Any]:
    """Ranked KPI comparison with percent deltas against the first scenario."""
    config = _area_or_error(area)
    if not scenarios:
        raise ValueError("at least one scenario is required")
    summaries = {
        scenario: load_scenario_summary(RESULTS_ROOT, config.name, scenario)
        for scenario in scenarios
    }
    return build_comparison(config.name, summaries)


def run_simulation(
    area: str,
    scenario: str = "baseline",
    window: str = "06:00-10:00",
    seed: int = 42,
    demand_factor: float = 0.75,
    signals: str | None = None,
) -> dict[str, Any]:
    """Run one SUMO scenario (takes minutes) and return its KPI summary."""
    config = _area_or_error(area)
    parsed = _parse_window(window)
    signals_path = _safe_repo_path(signals) if signals else None
    if signals_path is not None and not signals_path.is_file():
        raise ValueError(f"signal file not found: {signals}")
    summary = run_scenario(
        config,
        scenario=scenario,
        window=parsed,
        seed=seed,
        demand_factor=demand_factor,
        signals_path=signals_path,
        derived_root=DERIVED_ROOT,
        results_root=RESULTS_ROOT,
    )
    return {
        "scenario": scenario,
        "window": summary["window"],
        "seed": seed,
        "metering": summary.get("metering"),
        "signals": summary.get("signals"),
        "metrics": summary["metrics"],
    }


def optimize_signals(
    area: str,
    budget: str = "light",
    top: int = 8,
    confirm: bool = False,
    window: str = "06:00-10:00",
    eval_window: str = "06:00-08:00",
    seed: int = 42,
    workers: int = 4,
) -> dict[str, Any]:
    """Webster + GA signal optimization. Long-running (tens of minutes): needs confirm=true."""
    if not confirm:
        raise ValueError(
            "optimize_signals is long-running (~15-40 minutes); "
            "call again with confirm=true when you intend to run it"
        )
    config = _area_or_error(area)
    study = optimize_area_signals(
        config,
        budget=budget,
        top_k=top,
        window=_parse_window(window),
        eval_window=_parse_window(eval_window),
        seed=seed,
        workers=workers,
        derived_root=DERIVED_ROOT,
        results_root=RESULTS_ROOT,
    )
    return {
        "area": config.name,
        "selected": study["selected"],
        "common_cycle_s": study["common_cycle_s"],
        "ga": study["ga"],
        "offsets": study["offsets"],
        "signal_file": study["signal_file"],
        "validation": study["validation"],
    }


def render_report(area: str, scenarios: list[str], output: str | None = None) -> dict[str, Any]:
    """Render the comparison HTML report (seconds); output stays under results/ or docs/reports/."""
    config = _area_or_error(area)
    if not scenarios:
        raise ValueError("at least one scenario is required")
    output_path = (
        _safe_output_path(output) if output else RESULTS_ROOT / config.name / "report.html"
    )
    summaries = {
        scenario: load_scenario_summary(RESULTS_ROOT, config.name, scenario)
        for scenario in scenarios
    }
    comparison = build_comparison(config.name, summaries)
    figures: dict[str, str] = {}
    kpi_figure = build_kpi_figure(comparison)
    if kpi_figure:
        figures["kpis"] = kpi_figure
    throughput_figure = build_port_throughput_figure(RESULTS_ROOT, config.name, scenarios)
    if throughput_figure:
        figures["throughput"] = throughput_figure
    duration_figure = build_trip_duration_figure(RESULTS_ROOT, config.name, scenarios)
    if duration_figure:
        figures["durations"] = duration_figure
    render_html_report(output_path, comparison, figures)
    comparison_path = output_path.with_suffix(".json")
    comparison_path.write_text(json.dumps(comparison, indent=2, ensure_ascii=False) + "\n")
    return {
        "html": str(output_path.relative_to(REPO_ROOT)),
        "comparison_json": str(comparison_path.relative_to(REPO_ROOT)),
        "scenarios": scenarios,
    }


server.add_tool(list_areas)
server.add_tool(area_analysis)
server.add_tool(area_calibration)
server.add_tool(scenario_metrics)
server.add_tool(compare_scenarios)
server.add_tool(run_simulation)
server.add_tool(optimize_signals)
server.add_tool(render_report)


def main() -> None:
    """Run the MCP server over stdio."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
