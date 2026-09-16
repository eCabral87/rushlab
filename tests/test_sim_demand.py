"""Demand generation tests for SUMO."""

from __future__ import annotations

from pathlib import Path

import pytest

from rushlab.config import Area
from rushlab.demand.profile import normalized_profile
from rushlab.sim.demand import (
    DEFAULT_WINDOW,
    destination_edge,
    gateway_edges,
    plan_trips,
    route_trips,
    write_trips_xml,
)
from rushlab.sim.network import read_net

MINI_BBOX = (32.530, -117.045, 32.545, -117.015)
MINI_CROSSING = (32.5420, -117.0290)


def test_destination_edge_is_port_road(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    net = read_net(net_path)
    assert destination_edge(net, MINI_CROSSING) == "11"
    assert DEFAULT_WINDOW == (6, 10)


def test_gateway_detection(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    net = read_net(net_path)
    gateways = gateway_edges(net, MINI_BBOX, MINI_CROSSING)
    assert {gateway["edge"] for gateway in gateways} == {"10", "12"}
    assert all(gateway["lanes"] >= 1 for gateway in gateways)


def test_gateway_detection_filters_unreachable(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    net = read_net(net_path)
    assert gateway_edges(net, MINI_BBOX, MINI_CROSSING, destination="12") == []


def test_plan_trips_distribution_and_timing(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    net = read_net(net_path)
    gateways = gateway_edges(net, MINI_BBOX, MINI_CROSSING)
    calibration = {
        "volume": {"trailing_daily_average_veh": 43_200.0},
        "capacity_veh_h": {"central": 2720.0},
    }
    plan = plan_trips(gateways, "11", calibration, window=(6, 8), seed=7, demand_factor=1.0)
    profile = normalized_profile()
    expected_total = round(43_200.0 * (profile[6] + profile[7]))
    assert plan["total_vehicles"] == sum(plan["per_gateway"].values())
    assert abs(plan["total_vehicles"] - expected_total) <= 2 * 2
    assert plan["demand_factor"] == 1.0
    assert len(plan["trips"]) == plan["total_vehicles"]
    assert all(6 * 3600 <= trip["depart"] < 8 * 3600 for trip in plan["trips"])
    assert [trip["depart"] for trip in plan["trips"]] == sorted(
        trip["depart"] for trip in plan["trips"]
    )


def test_plan_trips_requires_gateways() -> None:
    with pytest.raises(ValueError, match="no gateway"):
        plan_trips([], "11", {"volume": {"trailing_daily_average_veh": 1.0}})


def test_route_trips(mini_area: Area, mini_net: tuple[Path, dict], tmp_path: Path) -> None:
    net_path, _ = mini_net
    trips = [
        {"id": "t0", "depart": 21_600.0, "from": "10", "to": "11"},
        {"id": "t1", "depart": 21_700.0, "from": "12", "to": "11"},
    ]
    trips_path = write_trips_xml(trips, tmp_path / "trips.xml")
    routes_path = tmp_path / "rou.xml"
    result = route_trips(trips_path, net_path, routes_path)
    assert result == {"requested": 2, "routed": 2}
    assert routes_path.is_file()
