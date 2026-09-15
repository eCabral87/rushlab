"""RushLab command line interface."""

from __future__ import annotations

import json
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from rushlab.config import Area, get_area, load_areas
from rushlab.demand.bts import (
    PERSONAL_VEHICLES,
    latest_month,
    load_volumes,
    trailing_daily_average,
)
from rushlab.demand.calibration import (
    calibrate,
    load_calibration,
    sink_overrides,
    write_calibration,
)
from rushlab.demand.cbp import append_snapshot, fetch_snapshot
from rushlab.network.build import BORDER_SINK, build_analysis_graph
from rushlab.network.fetch import fetch_area
from rushlab.network.metrics import analyze_area

app = typer.Typer(
    name="rushlab",
    help="Agent-driven traffic scenario lab for the San Ysidro border approach, Tijuana.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
RESULTS_ROOT = Path("results")
DERIVED_ROOT = Path("data/derived")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"rushlab {pkg_version('rushlab')}")
        raise typer.Exit()


@app.callback()
def main(
    _version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """RushLab CLI."""


def _area_or_exit(name: str) -> Area:
    try:
        return get_area(name)
    except KeyError as exc:
        console.print(f"[red]{exc.args[0]}[/red]")
        raise typer.Exit(code=2) from None


def _calibration_path(area_name: str) -> Path:
    return DERIVED_ROOT / area_name / "calibration.json"


def _sink_overrides(area_name: str) -> dict[str, float]:
    calibration = load_calibration(_calibration_path(area_name))
    return sink_overrides(calibration) if calibration else {}


@app.command()
def areas() -> None:
    """List registered study areas."""
    table = Table("area", "bbox (S,W,N,E)", "description")
    for area in load_areas().values():
        bbox = ", ".join(f"{value:g}" for value in area.bbox)
        table.add_row(area.name, bbox, area.description)
    console.print(table)


@app.command("fetch-area")
def fetch_area_command(
    name: str,
    refresh: bool = typer.Option(False, "--refresh", help="Re-download even when cached."),
) -> None:
    """Download the OSM drive network for a study area into the cache."""
    area = _area_or_exit(name)
    path = fetch_area(area, refresh=refresh)
    console.print(f"cached OSM graph: [bold]{path}[/bold]")


@app.command()
def demand(
    name: str,
    refresh: bool = typer.Option(False, "--refresh", help="Re-fetch BTS and CBP data."),
    snapshot: bool = typer.Option(
        True,
        "--snapshot/--no-snapshot",
        help="Append the current CBP reading to the committed wait-time series.",
    ),
) -> None:
    """Fetch demand data, calibrate the border sink, and write derived evidence."""
    area = _area_or_exit(name)
    frame = load_volumes(area, refresh=refresh)
    daily_average = trailing_daily_average(frame)
    vintage = latest_month(frame, PERSONAL_VEHICLES)
    cbp_snapshot = fetch_snapshot(area, refresh=refresh)
    if snapshot:
        appended = append_snapshot(cbp_snapshot, DERIVED_ROOT / area.name / "wait_snapshots.jsonl")
        console.print(f"CBP snapshot {'appended' if appended else 'already recorded'}")
    calibration = calibrate(
        area_name=area.name,
        daily_average_veh=daily_average,
        bts={"measure": PERSONAL_VEHICLES, "months": 12, "vintage": vintage},
        snapshot=cbp_snapshot,
    )
    out_path = write_calibration(_calibration_path(area.name), calibration)
    _print_calibration(calibration)
    console.print(f"wrote [bold]{out_path}[/bold]")


@app.command("build-area")
def build_area_command(
    name: str,
    refresh: bool = typer.Option(False, "--refresh", help="Re-download OSM data first."),
    calibrated: bool = typer.Option(
        True,
        "--calibrated/--no-calibrated",
        help="Use the derived sink calibration when available.",
    ),
) -> None:
    """Build the analytic graph for an area and print summary stats."""
    area = _area_or_exit(name)
    graphml = fetch_area(area, refresh=refresh)
    overrides = _sink_overrides(area.name) if calibrated else {}
    graph = build_analysis_graph(graphml, area=area, **overrides)
    sink = "yes" if BORDER_SINK in graph else "no"
    calibration = "calibrated" if overrides else "placeholder"
    console.print(
        f"{area.name}: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
        f"border sink attached: {sink} ({calibration} capacities)"
    )


@app.command()
def analyze(
    name: str,
    top: int = typer.Option(10, "--top", min=1, help="Rows per ranking."),
    refresh: bool = typer.Option(False, "--refresh", help="Re-download OSM data first."),
    calibrated: bool = typer.Option(
        True,
        "--calibrated/--no-calibrated",
        help="Use the derived sink calibration when available.",
    ),
) -> None:
    """Run resilience and bottleneck analysis; write results JSON."""
    area = _area_or_exit(name)
    graphml = fetch_area(area, refresh=refresh)
    overrides = _sink_overrides(area.name) if calibrated else {}
    graph = build_analysis_graph(graphml, area=area, **overrides)
    report = analyze_area(graph, area, top=top)
    report["calibration"] = "derived" if overrides else "placeholder"
    out_dir = RESULTS_ROOT / area.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "analysis.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    _print_report(report)
    console.print(f"wrote [bold]{out_path}[/bold]")


def _print_calibration(calibration: dict[str, Any]) -> None:
    volume = calibration["volume"]
    capacity = calibration["capacity_veh_h"]
    utilisation = calibration["utilisation_vs_peak"]
    observed = calibration["observed"]
    console.print(
        f"{calibration['area']}: BTS {volume['bts_vintage']} trailing daily average "
        f"{volume['trailing_daily_average_veh']:,.0f} {volume['measure']}"
    )
    console.print(
        f"peak-hour demand {calibration['peak_hour_demand_veh_h']:,.0f} veh/h | "
        f"max lanes {calibration['lanes']['max_pov']} | "
        f"capacity low/central/high: {capacity['low']:,.0f} / "
        f"{capacity['central']:,.0f} / {capacity['high']:,.0f} veh/h | "
        f"peak utilisation (central): {utilisation['central']:.2f}"
    )
    console.print(
        f"observed snapshot {observed['snapshot_date']} {observed['snapshot_time']}: "
        f"{observed['general_wait_s'] and observed['general_wait_s'] / 60:.0f} min wait, "
        f"{observed['general_lanes_open']} general lanes open"
        if observed["general_wait_s"]
        else f"observed snapshot {observed['snapshot_date']} {observed['snapshot_time']}"
    )


def _print_report(report: dict[str, Any]) -> None:
    connectivity = report["connectivity"]
    vulnerability = report["vulnerability"]
    border = report["border"]
    console.print(
        f"{report['area']}: {report['graph']['nodes']} nodes, {report['graph']['edges']} edges | "
        f"weak components: {connectivity['weak_components']} | "
        f"articulation points: {vulnerability['articulation_point_count']} | "
        f"bridges: {vulnerability['bridge_count']} | "
        f"calibration: {report.get('calibration', 'placeholder')}"
    )
    console.print(
        f"border reachable: {border['reachable_fraction']:.1%} | "
        f"median travel time to sink: {border['median_travel_time_to_sink_s']} s"
    )
    for terminal, value in border["min_cut_veh_h"].items():
        console.print(f"min cut {terminal} -> sink: {value:,.0f} veh/h")
    table = Table("rank", "node", "street", "betweenness", "signal")
    for rank, entry in enumerate(report["bottlenecks"]["top_nodes"], start=1):
        table.add_row(
            str(rank),
            str(entry["node"]),
            entry["name"] or "-",
            f"{entry['betweenness']:.4f}",
            "yes" if entry["signalized"] else "",
        )
    console.print(table)


if __name__ == "__main__":
    app()
