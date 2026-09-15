"""RushLab command line interface."""

from __future__ import annotations

from importlib.metadata import version as pkg_version

import typer

app = typer.Typer(
    name="rushlab",
    help="Agent-driven traffic scenario lab for the San Ysidro border approach, Tijuana.",
    no_args_is_help=True,
    add_completion=False,
)

AREAS = {"san-ysidro": "San Ysidro border approach (Tijuana), bbox 32.525,-117.06,32.555,-116.97"}

DATA_SOURCES = {
    "OpenStreetMap": "street network and signals (ODbL)",
    "BTS Border Crossing/Entry Data": "inbound vehicle volumes (public domain)",
    "CBP Border Wait Times": "wait-time profiles and lane service rates (public)",
}


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


@app.command()
def info() -> None:
    """Show registered study areas and data sources."""
    typer.echo("Study areas:")
    for name, description in AREAS.items():
        typer.echo(f"  {name}: {description}")
    typer.echo("Data sources:")
    for name, description in DATA_SOURCES.items():
        typer.echo(f"  {name}: {description}")


if __name__ == "__main__":
    app()
