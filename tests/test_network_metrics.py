"""Metric correctness tests on small hand-built graphs."""

from __future__ import annotations

import networkx as nx
import pytest

from rushlab.network.build import BORDER_SINK
from rushlab.network.metrics import (
    connectivity_summary,
    min_cut_to_sink,
    node_betweenness,
    signal_intersections,
    top_bottleneck_nodes,
    top_signal_bottlenecks,
    travel_time_to_sink,
    vulnerability_summary,
)


def bidirected(edges: list[tuple[int, int]]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for u, v in edges:
        graph.add_edge(u, v, travel_time_s=1.0)
        graph.add_edge(v, u, travel_time_s=1.0)
    return graph


def test_connectivity_summary_counts_components() -> None:
    graph = bidirected([(0, 1), (1, 2), (3, 4)])
    summary = connectivity_summary(graph)
    assert summary["weak_components"] == 2
    assert summary["largest_weak_fraction"] == pytest.approx(3 / 5)


def test_vulnerability_on_path() -> None:
    graph = bidirected([(0, 1), (1, 2), (2, 3), (3, 4)])
    summary = vulnerability_summary(graph)
    assert summary["articulation_point_count"] == 3
    assert summary["bridge_count"] == 4


def test_betweenness_on_path() -> None:
    graph = bidirected([(0, 1), (1, 2), (2, 3), (3, 4)])
    scores = node_betweenness(graph)
    assert scores[2] == pytest.approx(2 / 3)
    assert scores[1] == pytest.approx(0.5)
    assert scores[0] == pytest.approx(0.0)
    assert top_bottleneck_nodes(graph, top=1)[0]["node"] == 2


def test_min_cut_between_source_and_sink() -> None:
    graph = nx.DiGraph()
    graph.add_edge("A", "B", capacity_veh_h=10.0)
    graph.add_edge("A", "C", capacity_veh_h=3.0)
    graph.add_edge("C", "B", capacity_veh_h=5.0)
    assert min_cut_to_sink(graph, ["A"], sink="B") == pytest.approx(13.0)


def test_min_cut_rejects_empty_sources() -> None:
    graph = nx.DiGraph()
    graph.add_node(BORDER_SINK)
    with pytest.raises(ValueError, match="at least one source"):
        min_cut_to_sink(graph, [])


def test_travel_time_to_sink_requires_sink() -> None:
    graph = nx.DiGraph()
    graph.add_edge(1, 2, travel_time_s=5.0)
    with pytest.raises(KeyError, match="border_sink"):
        travel_time_to_sink(graph)


def test_signal_ranking() -> None:
    graph = bidirected([(0, 1), (1, 2), (2, 3), (3, 4)])
    graph.nodes[1]["highway"] = "traffic_signals"
    graph.nodes[2]["highway"] = "traffic_signals"
    assert set(signal_intersections(graph)) == {1, 2}
    top = top_signal_bottlenecks(graph, top=1)
    assert top[0]["node"] == 2
    assert top[0]["signalized"] is True
