"""Gateway detection and demand generation for SUMO microsimulation."""

from __future__ import annotations

import random
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

import sumolib

from rushlab.demand.profile import normalized_profile
from rushlab.network.build import haversine_m

BOUNDARY_MARGIN_DEG = 0.0008
DEFAULT_WINDOW = (6, 10)
# Share of port-bound demand represented by modeled main-road gateways.
DEFAULT_DEMAND_FACTOR = 0.75
EARTH_RADIUS_M = 6371000.0


def node_lonlat(net: sumolib.net.Net, node: Any) -> tuple[float, float]:
    lon, lat = net.convertXY2LonLat(*node.getCoord())
    return float(lon), float(lat)


def boundary_nodes(
    net: sumolib.net.Net,
    bbox: tuple[float, float, float, float],
    *,
    margin_deg: float = BOUNDARY_MARGIN_DEG,
) -> list[Any]:
    south, west, north, east = bbox
    selected = []
    for node in net.getNodes():
        lon, lat = node_lonlat(net, node)
        if (
            lat <= south + margin_deg
            or lat >= north - margin_deg
            or lon <= west + margin_deg
            or lon >= east - margin_deg
        ):
            selected.append(node)
    return selected


def destination_edge(
    net: sumolib.net.Net,
    crossing_point: tuple[float, float],
    *,
    radius_m: float = 800.0,
) -> str:
    """Normal edge closest to the border crossing point."""
    lat, lon = crossing_point
    best: tuple[float, str] | None = None
    for edge in net.getEdges(withInternal=False):
        if edge.getFunction():
            continue
        to_node = edge.getToNode()
        to_lon, to_lat = node_lonlat(net, to_node)
        distance = haversine_m(lat, lon, to_lat, to_lon)
        if distance <= radius_m and (best is None or distance < best[0]):
            best = (distance, edge.getID())
    if best is None:
        raise ValueError(f"no edge within {radius_m:.0f} m of crossing point ({lat}, {lon})")
    return best[1]


def reachable_source_edges(net: sumolib.net.Net, destination_edge: str) -> set[str]:
    """All edges that can topologically reach the destination edge."""
    if net.getEdge(destination_edge) is None:
        raise ValueError(f"destination edge {destination_edge!r} not in network")
    predecessors: dict[str, list[str]] = defaultdict(list)
    for edge in net.getEdges(withInternal=False):
        predecessors[edge.getToNode().getID()].append(edge.getID())
    seen = {destination_edge}
    stack = [destination_edge]
    while stack:
        edge_id = stack.pop()
        from_node = net.getEdge(edge_id).getFromNode().getID()
        for candidate in predecessors.get(from_node, ()):
            if candidate not in seen:
                seen.add(candidate)
                stack.append(candidate)
    return seen


def gateway_edges(
    net: sumolib.net.Net,
    bbox: tuple[float, float, float, float],
    crossing_point: tuple[float, float],
    *,
    margin_deg: float = BOUNDARY_MARGIN_DEG,
    destination: str | None = None,
) -> list[dict[str, Any]]:
    """Boundary edges whose direction heads toward the crossing (northbound entries).

    When ``destination`` is given, gateways that cannot reach it are dropped.
    """
    lat, lon = crossing_point
    reachable = reachable_source_edges(net, destination) if destination else None
    gateways: dict[str, dict[str, Any]] = {}
    for node in boundary_nodes(net, bbox, margin_deg=margin_deg):
        from_lon, from_lat = node_lonlat(net, node)
        from_distance = haversine_m(lat, lon, from_lat, from_lon)
        for edge in node.getOutgoing():
            if edge.getFunction() or edge.getLaneNumber() < 1:
                continue
            edge_id = edge.getID()
            if edge_id == destination:
                continue
            if reachable is not None and edge_id not in reachable:
                continue
            to_lon, to_lat = node_lonlat(net, edge.getToNode())
            to_distance = haversine_m(lat, lon, to_lat, to_lon)
            if to_distance >= from_distance:
                continue
            gateways[edge_id] = {
                "edge": edge_id,
                "from_node": node.getID(),
                "lanes": edge.getLaneNumber(),
                "distance_to_crossing_m": round(from_distance, 1),
            }
    return [gateways[edge_id] for edge_id in sorted(gateways)]


def _allocate(total: int, weights: dict[str, int]) -> dict[str, int]:
    """Largest-remainder allocation so rounded counts sum exactly to total."""
    weight_total = sum(weights.values())
    allocations = {key: int(total * weight / weight_total) for key, weight in weights.items()}
    remainder = total - sum(allocations.values())
    ranked = sorted(
        weights,
        key=lambda key: ((total * weights[key] / weight_total) - allocations[key], key),
        reverse=True,
    )
    for key in ranked[:remainder]:
        allocations[key] += 1
    return allocations


def plan_trips(
    gateways: list[dict[str, Any]],
    destination: str,
    calibration: dict[str, Any],
    *,
    window: tuple[int, int] = DEFAULT_WINDOW,
    seed: int = 42,
    demand_factor: float = DEFAULT_DEMAND_FACTOR,
) -> dict[str, Any]:
    """Distribute calibrated hourly demand over gateways and sample departures.

    ``demand_factor`` scales BTS volumes to the share represented by modeled
    main-road gateways (documented approximation; see ADR-0005).
    """
    if not gateways:
        raise ValueError("no gateway edges found")
    daily = float(calibration["volume"]["trailing_daily_average_veh"]) * demand_factor
    profile = normalized_profile()
    start_hour, end_hour = window
    hourly = {hour: daily * profile[hour] for hour in range(start_hour, end_hour)}
    weights = {gateway["edge"]: max(int(gateway["lanes"]), 1) for gateway in gateways}

    rng = random.Random(seed)
    trips: list[dict[str, Any]] = []
    per_gateway = {edge_id: 0 for edge_id in weights}
    index = 0
    for hour in range(start_hour, end_hour):
        hour_count = int(round(hourly[hour]))
        allocations = _allocate(hour_count, weights)
        for edge_id in sorted(allocations):
            per_gateway[edge_id] += allocations[edge_id]
            for _ in range(allocations[edge_id]):
                depart = hour * 3600 + rng.uniform(0.0, 3599.0)
                trips.append(
                    {
                        "id": f"t{index}",
                        "depart": round(depart, 1),
                        "from": edge_id,
                        "to": destination,
                    }
                )
                index += 1
    trips.sort(key=lambda trip: trip["depart"])
    return {
        "window": [start_hour, end_hour],
        "total_vehicles": len(trips),
        "demand_factor": demand_factor,
        "hourly_demand": {str(hour): round(value, 1) for hour, value in hourly.items()},
        "per_gateway": per_gateway,
        "trips": trips,
    }


def write_trips_xml(trips: list[dict[str, Any]], path: Path) -> Path:
    root = ET.Element("routes")
    ET.SubElement(root, "vType", id="car", vClass="passenger")
    for trip in trips:
        ET.SubElement(
            root,
            "trip",
            id=trip["id"],
            depart=str(trip["depart"]),
            **{"from": trip["from"], "to": trip["to"]},
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def route_trips(
    trips_path: Path, net_path: Path, out_path: Path, *, seed: int = 42
) -> dict[str, int]:
    """Route trips with duarouter; returns input/routed counts."""
    command = [
        "duarouter",
        "--net-file",
        str(net_path),
        "--route-files",
        str(trips_path),
        "--output-file",
        str(out_path),
        "--seed",
        str(seed),
        "--ignore-errors",
        "true",
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"duarouter failed:\n{result.stderr[-2000:]}")
    routed = len(ET.parse(out_path).getroot().findall("vehicle"))
    requested = len(ET.parse(trips_path).getroot().findall("trip"))
    return {"requested": requested, "routed": routed}
