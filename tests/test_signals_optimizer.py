"""GA offset optimization smoke test on the mini fixture (local SUMO)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from rushlab.signals import optimizer
from rushlab.signals.evaluator import EvaluatorConfig, evaluate_candidate
from rushlab.signals.flows import build_tls_flow_table
from rushlab.signals.optimizer import optimize_offsets
from rushlab.signals.programs import programs_from_table
from rushlab.sim.network import read_net


def build_routes(tmp_path: Path) -> Path:
    root = ET.Element("routes")
    ET.SubElement(root, "vType", id="car", vClass="passenger")
    for index in range(24):
        depart = 21900.0 + index * 25.0
        origin = "10" if index % 2 == 0 else "12"
        ET.SubElement(
            root,
            "trip",
            id=f"t{index}",
            depart=str(depart),
            **{"from": origin, "to": "11"},
        )
    path = tmp_path / "routes.rou.xml"
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def test_evaluate_candidate_runs_sumo(mini_net: tuple[Path, dict], tmp_path: Path) -> None:
    net_path, _ = mini_net
    routes = build_routes(tmp_path)
    net = read_net(net_path)
    junction = "2"
    phases = [
        {"duration": 30, "state": "GGGrr"},
        {"duration": 6, "state": "yyyrr"},
        {"duration": 30, "state": "rrrGG"},
        {"duration": 6, "state": "rrryy"},
    ]
    config = EvaluatorConfig(
        net_path=net_path,
        routes_path=routes,
        base_programs={junction: phases},
        working_root=tmp_path / "ga",
        begin_s=21600,
        end_s=25200,
        seed=1,
    )
    result = evaluate_candidate(config, {junction: 10.0})
    assert result["metrics"]["arrived"] > 0
    assert result["fitness"] < float("inf")
    assert net.getNode(junction).getType() == "traffic_light"


def test_ga_smoke_with_tiny_budget(
    mini_net: tuple[Path, dict], tmp_path: Path, monkeypatch
) -> None:
    net_path, _ = mini_net
    routes = build_routes(tmp_path)
    table = build_tls_flow_table(net_path, {"10": 900.0, "12": 1800.0}, window_hours=1.0)
    programs = programs_from_table(table, ["2"], {"2": (30.0, 30.0)})
    monkeypatch.setitem(optimizer.BUDGETS, "light", {"population": 4, "generations": 2})
    config = EvaluatorConfig(
        net_path=net_path,
        routes_path=routes,
        base_programs=programs,
        working_root=tmp_path / "ga",
        begin_s=21600,
        end_s=25200,
        seed=3,
    )
    result = optimize_offsets(config, ["2"], {"2": 66.0}, budget="light", seed=3, workers=1)
    assert set(result.offsets) == {"2"}
    assert 0.0 <= result.offsets["2"] < 66.0
    assert len(result.history) == 3
    assert result.evaluations >= 4
