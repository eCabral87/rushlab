"""Signal program serialization and selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sumolib

from rushlab.sim.metering import parse_net_structure


def build_tls_flow_ranking(
    net_path: Path, edge_flows: dict[str, float], *, exclude: set[str] | None = None
) -> list[tuple[str, float]]:
    """Traffic lights ranked by total measured approach flow."""
    structure = parse_net_structure(net_path)
    connections = structure["connections"]
    junctions = structure["junctions"]
    assert isinstance(connections, list) and isinstance(junctions, dict)
    excluded = exclude or set()
    inflow: dict[str, float] = {}
    seen: set[tuple[str, str]] = set()
    for connection in connections:
        tl = connection["tl"]
        if not tl or str(tl) in excluded:
            continue
        if junctions.get(str(tl)) != "traffic_light":
            continue
        edge_id = str(connection["from"] or "")
        pair = (str(tl), edge_id)
        if pair in seen:
            continue
        seen.add(pair)
        inflow[str(tl)] = inflow.get(str(tl), 0.0) + edge_flows.get(edge_id, 0.0)
    return sorted(inflow.items(), key=lambda item: item[1], reverse=True)


def programs_from_table(
    flow_table: dict[str, dict[str, Any]],
    junction_ids: list[str],
    greens_by_junction: dict[str, tuple[float, ...]],
) -> dict[str, list[dict]]:
    """Build retimed programs for the selected junctions."""
    programs: dict[str, list[dict]] = {}
    for junction_id in junction_ids:
        entry = flow_table[junction_id]
        from rushlab.signals.webster import retime_program

        programs[junction_id] = retime_program(
            entry["phases"], entry["green_positions"], list(greens_by_junction[junction_id])
        )
    return programs


def save_signal_file(
    path: Path,
    *,
    area: str,
    algorithm: str,
    cycle_s: float,
    programs: dict[str, list[dict]],
    offsets: dict[str, float],
    metadata: dict[str, Any] | None = None,
) -> Path:
    payload = {
        "area": area,
        "algorithm": algorithm,
        "cycle_s": cycle_s,
        "programs": programs,
        "offsets": offsets,
        "metadata": metadata or {},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return path


def load_signal_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def default_signal_path(cache_root: Path, area: str, name: str = "optimized") -> Path:
    return cache_root / area / "signals" / f"{name}.json"


def read_net_summary(net_path: Path) -> dict[str, int]:
    net = sumolib.net.readNet(str(net_path), withPrograms=False)
    return {
        "nodes": len(net.getNodes()),
        "edges": len(net.getEdges(withInternal=False)),
        "traffic_lights": len(
            [node for node in net.getNodes() if node.getType() == "traffic_light"]
        ),
    }
