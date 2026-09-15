"""Graph-theoretic resilience and bottleneck metrics."""

from __future__ import annotations

from datetime import UTC, datetime
from statistics import median
from typing import Any

import networkx as nx

from rushlab.config import Area
from rushlab.network.build import BORDER_SINK, nearest_node

SAMPLING_THRESHOLD = 5000
SAMPLING_K = 500
DEFAULT_SEED = 42
INF_CAPACITY = 1e12


def connectivity_summary(graph: nx.DiGraph) -> dict[str, Any]:
    weak = list(nx.weakly_connected_components(graph))
    strong = list(nx.strongly_connected_components(graph))
    largest = max((len(component) for component in weak), default=0)
    nodes = graph.number_of_nodes()
    return {
        "weak_components": len(weak),
        "strong_components": len(strong),
        "largest_weak_fraction": largest / nodes if nodes else 0.0,
    }


def vulnerability_summary(graph: nx.DiGraph) -> dict[str, Any]:
    """Articulation points and bridges are computed on the undirected view."""
    undirected = graph.to_undirected()
    return {
        "articulation_point_count": len(list(nx.articulation_points(undirected))),
        "bridge_count": len(list(nx.bridges(undirected))),
    }


def node_betweenness(graph: nx.DiGraph, *, seed: int = DEFAULT_SEED) -> dict[Any, float]:
    k = SAMPLING_K if graph.number_of_nodes() > SAMPLING_THRESHOLD else None
    return nx.betweenness_centrality(graph, k=k, weight="travel_time_s", seed=seed)


def edge_betweenness(graph: nx.DiGraph, *, seed: int = DEFAULT_SEED) -> dict[Any, float]:
    k = SAMPLING_K if graph.number_of_nodes() > SAMPLING_THRESHOLD else None
    return nx.edge_betweenness_centrality(graph, k=k, weight="travel_time_s", seed=seed)


def node_name(graph: nx.DiGraph, node: Any, *, limit: int = 3) -> str:
    names: list[str] = []
    for _, _, data in graph.edges(node, data=True):
        name = str(data.get("name") or "")
        if name and name not in names:
            names.append(name)
    return " / ".join(names[:limit])


def _node_entry(
    graph: nx.DiGraph, node: Any, score: float, *, name_limit: int = 3
) -> dict[str, Any]:
    data = graph.nodes[node]
    return {
        "node": node,
        "name": node_name(graph, node, limit=name_limit),
        "lat": data.get("y"),
        "lon": data.get("x"),
        "signalized": data.get("highway") == "traffic_signals",
        "betweenness": round(score, 6),
    }


def top_bottleneck_nodes(
    graph: nx.DiGraph,
    *,
    top: int = 10,
    seed: int = DEFAULT_SEED,
    scores: dict[Any, float] | None = None,
) -> list[dict[str, Any]]:
    scores = scores if scores is not None else node_betweenness(graph, seed=seed)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [_node_entry(graph, node, score) for node, score in ranked[:top]]


def top_bottleneck_edges(
    graph: nx.DiGraph, *, top: int = 10, seed: int = DEFAULT_SEED
) -> list[dict[str, Any]]:
    scores = edge_betweenness(graph, seed=seed)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    results = []
    for (u, v), score in ranked[:top]:
        data = graph.edges[u, v]
        results.append(
            {
                "from": u,
                "to": v,
                "name": data.get("name", ""),
                "highway": data.get("highway", ""),
                "betweenness": round(score, 6),
                "travel_time_s": round(float(data.get("travel_time_s", 0.0)), 3),
            }
        )
    return results


def signal_intersections(graph: nx.DiGraph) -> list[Any]:
    return [
        node for node, data in graph.nodes(data=True) if data.get("highway") == "traffic_signals"
    ]


def top_signal_bottlenecks(
    graph: nx.DiGraph,
    *,
    top: int = 10,
    seed: int = DEFAULT_SEED,
    scores: dict[Any, float] | None = None,
) -> list[dict[str, Any]]:
    scores = scores if scores is not None else node_betweenness(graph, seed=seed)
    signals = signal_intersections(graph)
    ranked = sorted(
        ((node, scores.get(node, 0.0)) for node in signals),
        key=lambda item: item[1],
        reverse=True,
    )
    return [_node_entry(graph, node, score) for node, score in ranked[:top]]


def travel_time_to_sink(graph: nx.DiGraph, sink: str = BORDER_SINK) -> dict[Any, float]:
    """Travel time from every node toward the sink (northbound direction)."""
    if sink not in graph:
        raise KeyError(f"sink {sink!r} not in graph; build with build_analysis_graph(area=...)")
    reversed_graph = graph.reverse(copy=False)
    return nx.single_source_dijkstra_path_length(reversed_graph, sink, weight="travel_time_s")


def min_cut_to_sink(graph: nx.DiGraph, sources: list[Any], *, sink: str = BORDER_SINK) -> float:
    """Minimum capacity (veh/h) separating the given sources from the sink."""
    if not sources:
        raise ValueError("at least one source is required")
    work = graph.copy()
    super_source = "__super_source__"
    work.add_node(super_source, x=None, y=None, highway="", street_count=0)
    for source in sources:
        work.add_edge(
            super_source,
            source,
            capacity_veh_h=INF_CAPACITY,
            travel_time_s=0.0,
            name="",
            highway="",
            lanes=None,
        )
    value, _ = nx.minimum_cut(work, super_source, sink, capacity="capacity_veh_h")
    return float(value)


def terminal_nodes(graph: nx.DiGraph, area: Area) -> dict[str, dict[str, Any]]:
    attached: dict[str, dict[str, Any]] = {}
    for terminal in area.terminals:
        node, distance = nearest_node(graph, *terminal.coordinates)
        if node is None:
            raise ValueError(f"terminal {terminal.name!r} could not be attached")
        attached[terminal.name] = {"node": node, "distance_m": round(distance, 1)}
    return attached


def analyze_area(
    graph: nx.DiGraph, area: Area, *, top: int = 10, seed: int = DEFAULT_SEED
) -> dict[str, Any]:
    scores = node_betweenness(graph, seed=seed)
    sink_distances = travel_time_to_sink(graph)
    finite = [distance for node, distance in sink_distances.items() if node != BORDER_SINK]
    total_nodes = graph.number_of_nodes()
    cuts = {
        name: min_cut_to_sink(graph, [info["node"]])
        for name, info in terminal_nodes(graph, area).items()
    }
    return {
        "area": area.name,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "graph": {"nodes": total_nodes, "edges": graph.number_of_edges()},
        "connectivity": connectivity_summary(graph),
        "vulnerability": vulnerability_summary(graph),
        "bottlenecks": {
            "top_nodes": top_bottleneck_nodes(graph, top=top, scores=scores),
            "top_edges": top_bottleneck_edges(graph, top=top, seed=seed),
        },
        "signals": {
            "count": len(signal_intersections(graph)),
            "top": top_signal_bottlenecks(graph, top=top, scores=scores),
        },
        "border": {
            "reachable_fraction": len(sink_distances) / total_nodes if total_nodes else 0.0,
            "median_travel_time_to_sink_s": round(median(finite), 1) if finite else None,
            "min_cut_veh_h": {name: round(value, 1) for name, value in cuts.items()},
        },
        "assumptions": [
            "Free-flow speeds: maxspeed tags with highway-class fallback (DEFAULT_SPEEDS).",
            "Capacity proxy: lanes x 1800 veh/h, lane defaults by class when untagged.",
            "Sink capacity and 30 s connector delay are placeholders until D4 calibration.",
            "Betweenness sampled with k=500 when the graph exceeds 5000 nodes.",
        ],
    }
