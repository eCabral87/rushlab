"""Analytic graph construction tests using the mini fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from rushlab.config import Area, BorderConfig
from rushlab.network.build import BORDER_SINK, build_analysis_graph, parse_lanes
from rushlab.network.metrics import travel_time_to_sink

FIXTURE = Path(__file__).parent / "fixtures" / "mini.graphml"
CROSSING = (32.5405, -117.0001)


def mini_area(capacity: float = 2400.0) -> Area:
    return Area(
        name="mini",
        description="test fixture",
        bbox=(32.53, -117.04, 32.55, -117.00),
        border=BorderConfig(
            name="Mini POE",
            crossing_points=(CROSSING,),
            sink_capacity_veh_h=capacity,
            lane_types=("general",),
        ),
    )


@pytest.fixture()
def graph():
    return build_analysis_graph(FIXTURE)


@pytest.fixture()
def border_graph():
    return build_analysis_graph(FIXTURE, area=mini_area())


def test_parallel_edges_collapse_to_fastest(graph) -> None:
    edge = graph[102][103]
    assert edge["travel_time_s"] == pytest.approx(22.5)
    assert edge["speed_kph"] == pytest.approx(80.0)
    assert edge["name"] == "Via Rapida"


def test_speed_fallback_by_highway_class(graph) -> None:
    edge = graph[103][104]
    assert edge["speed_kph"] == pytest.approx(40.0)  # secondary fallback
    assert edge["travel_time_s"] == pytest.approx(27.0)


def test_travel_times_and_capacity(graph) -> None:
    assert graph[101][102]["travel_time_s"] == pytest.approx(60.0)
    assert graph[101][102]["capacity_veh_h"] == pytest.approx(3600.0)
    assert graph[101][103]["speed_kph"] == pytest.approx(35.0)  # tertiary fallback


def test_oneway_not_reversed(graph) -> None:
    assert graph.has_edge(103, 104)
    assert not graph.has_edge(104, 103)


def test_border_sink_attachment(border_graph) -> None:
    assert BORDER_SINK in border_graph
    edge = border_graph[104][BORDER_SINK]
    assert edge["capacity_veh_h"] == pytest.approx(2400.0)
    assert edge["name"] == "Mini POE"


def test_travel_time_to_sink(border_graph) -> None:
    distances = travel_time_to_sink(border_graph)
    assert distances[104] == pytest.approx(30.0)
    assert distances[102] == pytest.approx(79.5)
    assert distances[101] == pytest.approx(139.5)


def test_parse_lanes() -> None:
    assert parse_lanes(None) is None
    assert parse_lanes("2") == 2
    assert parse_lanes("2;3") == 2
    assert parse_lanes(["4"]) == 4
    assert parse_lanes("no lanes") is None


def test_missing_crossing_node_raises() -> None:
    area = Area(
        name="off-map",
        description="",
        bbox=(0.0, 0.0, 1.0, 1.0),
        border=BorderConfig(
            name="nowhere",
            crossing_points=((0.0, 0.0),),
            sink_capacity_veh_h=1.0,
        ),
    )
    with pytest.raises(ValueError, match="no graph node within"):
        build_analysis_graph(FIXTURE, area=area)
