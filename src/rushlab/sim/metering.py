"""Fixed-time port metering signal derived from calibrated capacity."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

SATURATION_FLOW_VEH_H_PER_LANE = 1800.0
MAX_GREEN_RATIO = 0.95
MIN_GREEN_S = 8.0


@dataclass(frozen=True)
class MeteringTarget:
    junction_id: str
    link_indices: tuple[int, ...]
    lanes_to_port: int
    phases: tuple[dict[str, str | float], ...]
    approach_edges: tuple[str, ...] = ()


def parse_net_structure(net_path: Path) -> dict[str, object]:
    """Parse junctions, edges, connections, and tlLogic from a net file."""
    root = ET.parse(net_path).getroot()
    junctions = {element.get("id"): element.get("type") for element in root.findall("junction")}
    edge_from: dict[str, str] = {}
    edge_to: dict[str, str] = {}
    for element in root.findall("edge"):
        if element.get("function"):
            continue
        edge_from[str(element.get("id"))] = str(element.get("from"))
        edge_to[str(element.get("id"))] = str(element.get("to"))
    connections = []
    for element in root.findall("connection"):
        link_index = element.get("linkIndex")
        connections.append(
            {
                "from": element.get("from"),
                "to": element.get("to"),
                "tl": element.get("tl"),
                "link_index": int(link_index) if link_index is not None else None,
            }
        )
    tl_logic: dict[str, list[dict[str, str | float]]] = {}
    for logic in root.findall("tlLogic"):
        tl_logic[str(logic.get("id"))] = [
            {
                "duration": float(phase.get("duration", 0)),
                "state": phase.get("state", ""),
                "name": phase.get("name") or "",
            }
            for phase in logic.findall("phase")
        ]
    return {
        "junctions": junctions,
        "edge_from": edge_from,
        "edge_to": edge_to,
        "connections": connections,
        "tl_logic": tl_logic,
    }


def find_metering_target(
    net_path: Path, destination_edge: str, *, max_hops: int = 3
) -> MeteringTarget | None:
    """First traffic-light junction upstream of the destination edge."""
    data = parse_net_structure(net_path)
    junctions = data["junctions"]
    edge_from = data["edge_from"]
    edge_to = data["edge_to"]
    connections = data["connections"]
    tl_logic = data["tl_logic"]
    assert isinstance(junctions, dict) and isinstance(edge_from, dict)
    assert isinstance(edge_to, dict) and isinstance(connections, list)
    assert isinstance(tl_logic, dict)

    incoming: dict[str, list[str]] = defaultdict(list)
    for edge_id, to_node in edge_to.items():
        incoming[to_node].append(edge_id)

    frontier = {destination_edge}
    visited: set[str] = set()
    for _ in range(max_hops + 1):
        next_frontier: set[str] = set()
        for edge_id in sorted(frontier):
            if edge_id in visited:
                continue
            visited.add(edge_id)
            junction = edge_from.get(edge_id)
            if junction is None:
                continue
            if junctions.get(junction) == "traffic_light":
                port_links = [
                    connection
                    for connection in connections
                    if connection["tl"] == junction
                    and connection["to"] == edge_id
                    and connection["link_index"] is not None
                ]
                link_indices = tuple(sorted(connection["link_index"] for connection in port_links))
                if link_indices:
                    approach_edges = tuple(
                        sorted(
                            {
                                str(connection["from"])
                                for connection in port_links
                                if connection["from"]
                            }
                        )
                    )
                    return MeteringTarget(
                        junction_id=junction,
                        link_indices=link_indices,
                        lanes_to_port=len(link_indices),
                        phases=tuple(tl_logic.get(junction, [])),
                        approach_edges=approach_edges,
                    )
            next_frontier.update(incoming.get(junction, []))
        frontier = next_frontier
    return None


def metering_program(
    phases: tuple[dict[str, str | float], ...],
    link_indices: tuple[int, ...],
    target_veh_h: float,
    lanes_to_port: int,
    *,
    saturation_flow: float = SATURATION_FLOW_VEH_H_PER_LANE,
    max_ratio: float = MAX_GREEN_RATIO,
    min_green_s: float = MIN_GREEN_S,
) -> list[dict[str, str | float]] | None:
    """Retime the port phases so the metered movement matches target throughput.

    The junction's natural capacity is lane-weighted per phase; metering only
    reduces it. Returns ``None`` when the target is already unreachable upward
    (the junction geometry, not the signal plan, is the binding constraint).
    """
    if not phases or not link_indices or lanes_to_port < 1:
        return None

    def green_links(phase: dict[str, str | float]) -> int:
        state = str(phase["state"])
        return sum(1 for index in link_indices if index < len(state) and state[index] == "G")

    port_positions = [index for index, phase in enumerate(phases) if green_links(phase)]
    if not port_positions:
        return None

    total_duration = sum(float(phase["duration"]) for phase in phases)
    port_duration = sum(float(phases[index]["duration"]) for index in port_positions)
    lane_green = sum(
        float(phases[index]["duration"]) * green_links(phases[index]) for index in port_positions
    )
    rest_duration = total_duration - port_duration
    natural_capacity = saturation_flow * lane_green / total_duration
    if target_veh_h >= natural_capacity:
        return None

    denominator = saturation_flow * lane_green - target_veh_h * port_duration
    if denominator <= 0:
        return None
    scale = target_veh_h * rest_duration / denominator

    program: list[dict[str, str | float]] = []
    for index, phase in enumerate(phases):
        duration = float(phase["duration"])
        if index in port_positions:
            duration = max(duration * scale, min_green_s)
            cycle_so_far = rest_duration + duration
            ratio = duration / cycle_so_far if cycle_so_far else 0.0
            if ratio > max_ratio:
                duration = max_ratio * rest_duration / (1.0 - max_ratio)
        program.append(
            {
                "duration": round(duration, 1),
                "state": str(phase["state"]),
                "name": str(phase.get("name", "")),
            }
        )
    return program


def program_summary(
    program: list[dict[str, str | float]], link_indices: tuple[int, ...], lanes_to_port: int
) -> dict[str, float]:
    def green_links(phase: dict[str, str | float]) -> int:
        state = str(phase["state"])
        return sum(1 for index in link_indices if index < len(state) and state[index] == "G")

    cycle = sum(float(phase["duration"]) for phase in program)
    lane_green = sum(float(phase["duration"]) * green_links(phase) for phase in program)
    port_green = sum(float(phase["duration"]) for phase in program if green_links(phase) > 0)
    lane_ratio = lane_green / cycle if cycle else 0.0
    return {
        "cycle_s": round(cycle, 1),
        "port_green_s": round(port_green, 1),
        "port_green_ratio": round(port_green / cycle, 3) if cycle else 0.0,
        "estimated_capacity_veh_h": round(lane_ratio * SATURATION_FLOW_VEH_H_PER_LANE, 1),
    }


def apply_programs_to_net(
    net_path: Path,
    programs: dict[str, list[dict]],
    output_path: Path,
    *,
    offsets: dict[str, float] | None = None,
) -> Path:
    """Replace one or more junction tlLogic programs in a net file.

    Offsets are written to the ``offset`` attribute of the tlLogic element.
    """
    tree = ET.parse(net_path)
    root = tree.getroot()
    logics = {logic.get("id"): logic for logic in root.findall("tlLogic")}
    missing = sorted(junction for junction in programs if junction not in logics)
    if missing:
        raise ValueError(f"traffic lights not found in net: {missing}")
    for junction_id, phases in programs.items():
        logic = logics[junction_id]
        for phase in list(logic.findall("phase")):
            logic.remove(phase)
        for phase in phases:
            attributes = {
                "duration": str(phase["duration"]),
                "state": str(phase["state"]),
            }
            if phase.get("name"):
                attributes["name"] = str(phase["name"])
            ET.SubElement(logic, "phase", attrib=attributes)
        if offsets is not None and junction_id in offsets:
            logic.set("offset", str(offsets[junction_id]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    return output_path


def apply_program_to_net(
    net_path: Path, junction_id: str, program: list[dict], output_path: Path
) -> Path:
    """Single-junction convenience wrapper around :func:`apply_programs_to_net`.

    Patching the generated net avoids netconvert's ordering limitation where
    ``--tllogic-files`` is loaded before ``--tls.set`` creates the junction.
    """
    return apply_programs_to_net(net_path, {junction_id: program}, output_path)


def write_tllogic_file(path: Path, target: MeteringTarget, program: list[dict]) -> Path:
    root = ET.Element("tlLogics")
    logic = ET.SubElement(
        root,
        "tlLogic",
        id=target.junction_id,
        type="static",
        programID="0",
        offset="0",
    )
    for phase in program:
        attributes = {
            "duration": str(phase["duration"]),
            "state": str(phase["state"]),
        }
        if phase.get("name"):
            attributes["name"] = str(phase["name"])
        ET.SubElement(logic, "phase", attrib=attributes)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path
