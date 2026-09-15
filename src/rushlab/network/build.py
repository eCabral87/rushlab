"""Build the analytic road graph from cached OSM data."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import networkx as nx
import osmnx as ox

from rushlab.config import Area

# Fallback free-flow speeds (km/h) by OSM highway class when maxspeed is absent.
# Conservative urban values; documented in ADR-0003.
DEFAULT_SPEEDS: dict[str, float] = {
    "motorway": 90.0,
    "motorway_link": 60.0,
    "trunk": 70.0,
    "trunk_link": 50.0,
    "primary": 50.0,
    "primary_link": 40.0,
    "secondary": 40.0,
    "secondary_link": 30.0,
    "tertiary": 35.0,
    "tertiary_link": 25.0,
    "unclassified": 30.0,
    "residential": 25.0,
    "living_street": 15.0,
    "service": 15.0,
}
FALLBACK_SPEED_KPH = 25.0

# Lane-count defaults by class for the capacity proxy; documented in ADR-0003.
DEFAULT_LANES: dict[str, int] = {
    "motorway": 3,
    "motorway_link": 1,
    "trunk": 2,
    "trunk_link": 1,
    "primary": 2,
    "primary_link": 1,
    "secondary": 2,
    "secondary_link": 1,
    "tertiary": 1,
    "tertiary_link": 1,
    "unclassified": 1,
    "residential": 1,
    "living_street": 1,
    "service": 1,
}
SATURATION_FLOW_VEH_H_PER_LANE = 1800.0

BORDER_SINK = "border_sink"
SINK_SEARCH_RADIUS_M = 600.0
# Placeholder crossing delay for sink connectors until D4 calibration.
SINK_CONNECTOR_DELAY_S = 30.0
EARTH_RADIUS_M = 6371000.0
NODE_ATTRS = ("x", "y", "highway", "street_count")


def load_osm_graph(path: Path) -> nx.MultiDiGraph:
    return ox.load_graphml(path)


def edge_name(data: dict[str, Any]) -> str:
    """Edge names can be strings or lists after GraphML round-trips."""
    name = data.get("name")
    if isinstance(name, list):
        return ", ".join(str(part) for part in name)
    return "" if name is None else str(name)


def parse_lanes(value: object) -> int | None:
    """Parse OSM lane counts like ``2``, ``"2"``, ``"2;3"`` or ``["2"]``."""
    if value is None:
        return None
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]
    digits = ""
    for char in str(value):
        if char.isdigit():
            digits += char
        elif digits:
            break
    return int(digits) if digits else None


def edge_capacity_veh_h(data: dict[str, Any]) -> float:
    lanes = parse_lanes(data.get("lanes"))
    if lanes is None:
        lanes = DEFAULT_LANES.get(str(data.get("highway", "")), 1)
    return lanes * SATURATION_FLOW_VEH_H_PER_LANE


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def nearest_node(graph: nx.DiGraph, lat: float, lon: float) -> tuple[Any | None, float]:
    best_node: Any | None = None
    best_distance = math.inf
    for node, data in graph.nodes(data=True):
        y, x = data.get("y"), data.get("x")
        if y is None or x is None:
            continue
        distance = haversine_m(lat, lon, float(y), float(x))
        if distance < best_distance:
            best_node, best_distance = node, distance
    return best_node, best_distance


def _edge_attributes(data: dict[str, Any], travel_time: float) -> dict[str, Any]:
    return {
        "travel_time_s": travel_time,
        "length_m": float(data["length"]),
        "speed_kph": float(data["speed_kph"]),
        "name": edge_name(data),
        "highway": str(data.get("highway", "")),
        "lanes": parse_lanes(data.get("lanes")),
        "capacity_veh_h": edge_capacity_veh_h(data),
    }


def build_analysis_graph(source: Path | nx.MultiDiGraph, *, area: Area | None = None) -> nx.DiGraph:
    """Simplify an osmnx MultiDiGraph into a directed travel-time graph.

    Parallel edges collapse to the fastest one; all other attributes come from
    that edge. When ``area`` has border metadata, a synthetic sink is attached.
    """
    graph = load_osm_graph(source) if isinstance(source, Path) else source.copy()
    graph = ox.add_edge_speeds(graph, hwy_speeds=DEFAULT_SPEEDS, fallback=FALLBACK_SPEED_KPH)
    graph = ox.add_edge_travel_times(graph)

    digraph = nx.DiGraph()
    for node, data in graph.nodes(data=True):
        digraph.add_node(node, **{attr: data.get(attr) for attr in NODE_ATTRS})
    for u, v, data in graph.edges(data=True):
        travel_time = float(data["travel_time"])
        existing = digraph.get_edge_data(u, v)
        if existing is not None and existing["travel_time_s"] <= travel_time:
            continue
        digraph.add_edge(u, v, **_edge_attributes(data, travel_time))

    if area is not None and area.border is not None:
        attach_border_sink(digraph, area)
    return digraph


def attach_border_sink(
    graph: nx.DiGraph, area: Area, *, radius_m: float = SINK_SEARCH_RADIUS_M
) -> list[Any]:
    """Attach ``BORDER_SINK`` to the road nodes nearest each crossing point."""
    if area.border is None:
        raise ValueError("area has no border metadata")
    connectors: list[Any] = []
    for lat, lon in area.border.crossing_points:
        node, distance = nearest_node(graph, lat, lon)
        if node is None or distance > radius_m:
            raise ValueError(
                f"no graph node within {radius_m:.0f} m of crossing point ({lat}, {lon})"
            )
        connectors.append(node)
    connectors = sorted(set(connectors))

    mean_lat = sum(point[0] for point in area.border.crossing_points) / len(
        area.border.crossing_points
    )
    mean_lon = sum(point[1] for point in area.border.crossing_points) / len(
        area.border.crossing_points
    )
    graph.add_node(
        BORDER_SINK,
        x=mean_lon,
        y=mean_lat,
        highway="border",
        street_count=len(connectors),
    )
    capacity_each = area.border.sink_capacity_veh_h / len(connectors)
    for node in connectors:
        graph.add_edge(
            node,
            BORDER_SINK,
            travel_time_s=SINK_CONNECTOR_DELAY_S,
            length_m=0.0,
            speed_kph=0.0,
            name=area.border.name,
            highway="border",
            lanes=None,
            capacity_veh_h=capacity_each,
        )
    return connectors
