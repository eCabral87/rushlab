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


@app.command("build-area")
def build_area_command(
    name: str,
    refresh: bool = typer.Option(False, "--refresh", help="Re-download OSM data first."),
) -> None:
    """Build the analytic graph for an area and print summary stats."""
    area = _area_or_exit(name)
    graphml = fetch_area(area, refresh=refresh)
    graph = build_analysis_graph(graphml, area=area)
    sink = "yes" if BORDER_SINK in graph else "no"
    console.print(
        f"{area.name}: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
        f"border sink attached: {sink}"
    )


@app.command()
def analyze(
    name: str,
    top: int = typer.Option(10, "--top", min=1, help="Rows per ranking."),
    refresh: bool = typer.Option(False, "--refresh", help="Re-download OSM data first."),
) -> None:
    """Run resilience and bottleneck analysis; write results JSON."""
    area = _area_or_exit(name)
    graphml = fetch_area(area, refresh=refresh)
    graph = build_analysis_graph(graphml, area=area)
    report = analyze_area(graph, area, top=top)
    out_dir = RESULTS_ROOT / area.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "analysis.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    _print_report(report)
    console.print(f"wrote [bold]{out_path}[/bold]")


def _print_report(report: dict[str, Any]) -> None:
    connectivity = report["connectivity"]
    vulnerability = report["vulnerability"]
    border = report["border"]
    console.print(
        f"{report['area']}: {report['graph']['nodes']} nodes, {report['graph']['edges']} edges | "
        f"weak components: {connectivity['weak_components']} | "
        f"articulation points: {vulnerability['articulation_point_count']} | "
        f"bridges: {vulnerability['bridge_count']}"
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
