"""Per-signal approach flows and critical flow ratios from edgeData."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

import sumolib

from rushlab.sim.metering import parse_net_structure

SATURATION_FLOW_PER_LANE = 1800.0
STARTUP_LOST_TIME_S = 2.0


def load_edge_flows(edgedata_path: Path, *, attribute: str = "entered") -> dict[str, float]:
    """Total vehicles per edge over the analysis window (from edgeData)."""
    flows: dict[str, float] = defaultdict(float)
    for interval in ET.parse(edgedata_path).getroot().findall("interval"):
        for edge in interval.findall("edge"):
            edge_id = edge.get("id")
            if edge_id:
                flows[edge_id] += float(edge.get(attribute, 0))
    return dict(flows)


def build_tls_flow_table(
    net_path: Path,
    edge_flows: dict[str, float],
    *,
    window_hours: float = 1.0,
    saturation_flow: float = SATURATION_FLOW_PER_LANE,
    startup_lost_time_s: float = STARTUP_LOST_TIME_S,
) -> dict[str, dict[str, Any]]:
    """Critical flow ratio per green phase for every traffic light.

    Ratios are flow / (lanes x saturation flow) using veh/h values converted
    from the window totals.
    """
    if window_hours <= 0:
        raise ValueError("window_hours must be positive")
    structure = parse_net_structure(net_path)
    connections = structure["connections"]
    tl_logic = structure["tl_logic"]
    assert isinstance(connections, list) and isinstance(tl_logic, dict)

    net = sumolib.net.readNet(str(net_path), withPrograms=False)
    lanes_by_edge = {
        edge.getID(): edge.getLaneNumber() for edge in net.getEdges(withInternal=False)
    }

    by_tl: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for connection in connections:
        if connection["tl"]:
            by_tl[str(connection["tl"])].append(connection)

    table: dict[str, dict[str, Any]] = {}
    for junction_id, phases in tl_logic.items():
        links = by_tl.get(junction_id, [])
        if not links:
            continue
        green_positions: list[int] = []
        ratios: list[float] = []
        for position, phase in enumerate(phases):
            state = str(phase["state"])
            critical = 0.0
            saw_green = False
            for link in links:
                link_index = link["link_index"]
                if link_index is None or link_index >= len(state) or state[link_index] != "G":
                    continue
                saw_green = True
                edge_id = link["from"]
                if not edge_id:
                    continue
                flow = edge_flows.get(str(edge_id), 0.0) / window_hours
                lanes = max(lanes_by_edge.get(str(edge_id), 1), 1)
                critical = max(critical, flow / (lanes * saturation_flow))
            if saw_green:
                green_positions.append(position)
                ratios.append(critical)
        if not green_positions:
            continue
        approach_edges = {str(link["from"]) for link in links if link["from"]}
        approach_flow = sum(edge_flows.get(edge, 0.0) for edge in approach_edges)
        lost_time = sum(
            float(phase["duration"])
            for position, phase in enumerate(phases)
            if position not in green_positions
        ) + startup_lost_time_s * len(green_positions)
        table[junction_id] = {
            "green_positions": green_positions,
            "ratios": ratios,
            "lost_time_s": lost_time,
            "approach_flow": approach_flow,
            "phases": phases,
        }
    return table
