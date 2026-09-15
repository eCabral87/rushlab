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


def test_build_area_with_cached_fixture(monkeypatch) -> None:
    monkeypatch.setattr("rushlab.cli.fetch_area", lambda area, refresh=False: FIXTURE)
    result = runner.invoke(app, ["build-area", "san-ysidro"])
    assert result.exit_code == 0
    assert "border sink attached: yes" in result.stdout


def test_analyze_writes_report(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("rushlab.cli.fetch_area", lambda area, refresh=False: FIXTURE)
    monkeypatch.setattr("rushlab.cli.RESULTS_ROOT", tmp_path)
    result = runner.invoke(app, ["analyze", "san-ysidro", "--top", "3"])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "san-ysidro" / "analysis.json").is_file()
