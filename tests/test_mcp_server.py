"""MCP server tool tests, including an in-memory client round trip."""

from __future__ import annotations

import asyncio
import contextlib
import json
from pathlib import Path

import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_client_server_memory_streams

from rushlab import mcp_server
from rushlab.demand.calibration import write_calibration

EXPECTED_TOOLS = {
    "list_areas",
    "area_analysis",
    "area_calibration",
    "scenario_metrics",
    "compare_scenarios",
    "run_simulation",
    "optimize_signals",
    "render_report",
}


@pytest.fixture()
def mcp_paths(tmp_path: Path, monkeypatch) -> Path:
    monkeypatch.setattr(mcp_server, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mcp_server, "RESULTS_ROOT", tmp_path / "results")
    monkeypatch.setattr(mcp_server, "REPORTS_ROOT", tmp_path / "docs" / "reports")
    monkeypatch.setattr(mcp_server, "DERIVED_ROOT", tmp_path / "data" / "derived")
    monkeypatch.setattr(mcp_server, "OSM_CACHE_ROOT", tmp_path / "data" / "cache" / "areas")
    return tmp_path


def write_summary(
    results_root: Path,
    area: str,
    scenario: str,
    *,
    time_loss: float = 100.0,
    throughput: float = 1000.0,
) -> None:
    directory = results_root / area / "sumo" / scenario
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "summary.json").write_text(
        json.dumps(
            {
                "area": area,
                "scenario": scenario,
                "window": "06:00-10:00",
                "seed": 42,
                "plan": {"total_vehicles": 100, "demand_factor": 0.75},
                "metering": {"junction": "2"},
                "signals": None,
                "destination_edge": "11",
                "metrics": {
                    "mean_trip_time_loss_s": time_loss,
                    "mean_trip_duration_s": time_loss + 100,
                    "port_throughput_veh_h": throughput,
                    "port_throughput_peak_veh_h": throughput + 100,
                    "port_approach_waiting_time_s": time_loss * 2,
                    "teleports": 5,
                    "arrived": 90,
                    "inserted": 95,
                },
            }
        )
    )


def test_list_areas_includes_san_ysidro() -> None:
    areas = mcp_server.list_areas()
    assert any(area["name"] == "san-ysidro" for area in areas)
    assert all("bbox" in area for area in areas)


def test_area_calibration_missing_raises(mcp_paths: Path) -> None:
    with pytest.raises(RuntimeError, match="no calibration"):
        mcp_server.area_calibration("san-ysidro")


def test_area_calibration_roundtrip(mcp_paths: Path) -> None:
    write_calibration(
        mcp_paths / "data" / "derived" / "san-ysidro" / "calibration.json",
        {"area": "san-ysidro", "volume": {"trailing_daily_average_veh": 43057.0}},
    )
    calibration = mcp_server.area_calibration("san-ysidro")
    assert calibration["volume"]["trailing_daily_average_veh"] == 43057.0


def test_area_analysis_requires_cached_graph(mcp_paths: Path) -> None:
    with pytest.raises(RuntimeError, match="cached OSM graph"):
        mcp_server.area_analysis("san-ysidro")


def test_scenario_metrics(mcp_paths: Path) -> None:
    write_summary(mcp_paths / "results", "san-ysidro", "baseline")
    payload = mcp_server.scenario_metrics("san-ysidro", "baseline")
    assert payload["metrics"]["mean_trip_time_loss_s"] == 100.0
    assert payload["metering"] == {"junction": "2"}


def test_compare_scenarios_deltas(mcp_paths: Path) -> None:
    write_summary(mcp_paths / "results", "san-ysidro", "baseline", time_loss=100.0)
    write_summary(mcp_paths / "results", "san-ysidro", "optimized", time_loss=80.0)
    comparison = mcp_server.compare_scenarios("san-ysidro", ["baseline", "optimized"])
    rows = {row["key"]: row for row in comparison["rows"]}
    assert rows["mean_trip_time_loss_s"]["delta_pct"]["optimized"] == -20.0


def test_render_report_writes_files(mcp_paths: Path) -> None:
    write_summary(mcp_paths / "results", "san-ysidro", "baseline")
    result = mcp_server.render_report(
        "san-ysidro", ["baseline"], output="results/san-ysidro/report.html"
    )
    assert (mcp_paths / result["html"]).is_file()
    assert (mcp_paths / result["comparison_json"]).is_file()


def test_render_report_rejects_outside_paths(mcp_paths: Path) -> None:
    with pytest.raises(ValueError, match="must stay under"):
        mcp_server.render_report("san-ysidro", ["baseline"], output="etc/evil.html")


def test_run_simulation_parses_window_and_delegates(mcp_paths: Path, monkeypatch) -> None:
    captured: dict = {}

    def fake_run_scenario(area, **kwargs):
        captured["area"] = area.name
        captured.update(kwargs)
        return {
            "window": "07:00-09:00",
            "metrics": {"teleports": 0},
            "metering": None,
            "signals": None,
        }

    monkeypatch.setattr(mcp_server, "run_scenario", fake_run_scenario)
    result = mcp_server.run_simulation("san-ysidro", window="07:00-09:00", seed=7)
    assert captured["window"] == (7, 9)
    assert captured["seed"] == 7
    assert result["metrics"] == {"teleports": 0}
    with pytest.raises(ValueError, match="window"):
        mcp_server.run_simulation("san-ysidro", window="10:00-06:00")


def test_optimize_signals_requires_confirm(mcp_paths: Path, monkeypatch) -> None:
    with pytest.raises(ValueError, match="confirm=true"):
        mcp_server.optimize_signals("san-ysidro")

    def fake_optimize(area, **kwargs):
        return {
            "selected": ["a"],
            "common_cycle_s": 60.0,
            "ga": {"budget": "light", "evaluations": 1, "best_fitness": 1.0, "history": []},
            "offsets": {"a": 1.0},
            "signal_file": "cache/signals.json",
            "validation": {"metrics": {}},
        }

    monkeypatch.setattr(mcp_server, "optimize_area_signals", fake_optimize)
    result = mcp_server.optimize_signals("san-ysidro", confirm=True)
    assert result["selected"] == ["a"]


def _with_client(call):
    async def runner():
        async with create_client_server_memory_streams() as (client_streams, server_streams):
            read_stream, write_stream = server_streams
            lowlevel = mcp_server.server._lowlevel_server
            task = asyncio.create_task(
                lowlevel.run(read_stream, write_stream, lowlevel.create_initialization_options())
            )
            try:
                async with ClientSession(*client_streams) as client:
                    await client.initialize()
                    return await call(client)
            finally:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

    return asyncio.run(runner())


def test_in_memory_client_lists_and_calls_tools() -> None:
    async def call(client):
        tools = await client.list_tools()
        names = {tool.name for tool in tools.tools}
        result = await client.call_tool("list_areas", {})
        return names, result.content[0].text

    names, text = _with_client(call)
    assert names == EXPECTED_TOOLS
    assert "san-ysidro" in text


@pytest.mark.integration
def test_stdio_server_lists_tools() -> None:
    from mcp.client.stdio import StdioServerParameters, stdio_client

    repo_root = Path(__file__).resolve().parents[1]

    async def runner():
        params = StdioServerParameters(
            command="uv",
            args=["run", "--no-sync", "rushlab-mcp"],
            cwd=str(repo_root),
        )
        async with (
            stdio_client(params) as (read_stream, write_stream),
            ClientSession(read_stream, write_stream) as client,
        ):
            await client.initialize()
            tools = await client.list_tools()
            return {tool.name for tool in tools.tools}

    assert _with_stdio(runner) == EXPECTED_TOOLS


def _with_stdio(runner):
    return asyncio.run(runner())
