"""CLI smoke tests."""

from typer.testing import CliRunner

from rushlab import __version__
from rushlab.cli import app

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_info_lists_study_area() -> None:
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "san-ysidro" in result.stdout
