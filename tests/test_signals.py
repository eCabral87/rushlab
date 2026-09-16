"""Signal flow, Webster, and program tests on the mini fixture."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from rushlab.signals.flows import build_tls_flow_table, load_edge_flows
from rushlab.signals.programs import (
    build_tls_flow_ranking,
    load_signal_file,
    programs_from_table,
    save_signal_file,
)
from rushlab.signals.webster import (
    plan_with_cycle,
    retime_program,
    webster_plan,
)
from rushlab.sim.metering import apply_programs_to_net


def write_edgedata(path: Path, flows: dict[str, float]) -> Path:
    root = ET.Element("edgedata")
    interval = ET.SubElement(root, "interval", begin="0", end="3600")
    for edge_id, value in flows.items():
        ET.SubElement(interval, "edge", id=edge_id, entered=str(value), arrived="0")
    path.write_text(ET.tostring(root, encoding="unicode"))
    return path


def test_load_edge_flows(tmp_path: Path) -> None:
    path = write_edgedata(tmp_path / "edgedata.xml", {"10": 100, "12": 250})
    flows = load_edge_flows(path)
    assert flows == {"10": 100.0, "12": 250.0}


def test_tls_flow_table_ratios(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    table = build_tls_flow_table(net_path, {"10": 900.0, "12": 1800.0}, window_hours=1.0)
    entry = table["2"]
    assert entry["green_positions"] == [0, 2]
    assert entry["ratios"] == pytest.approx([0.5, 0.25])
    assert entry["lost_time_s"] == pytest.approx(16.0)  # 6 + 6 yellow + 2 x 2 startup
    assert entry["approach_flow"] == pytest.approx(2700.0)


def test_flow_ranking_excludes_port(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    ranking = build_tls_flow_ranking(net_path, {"10": 900.0, "12": 1800.0})
    assert ranking == [("2", pytest.approx(2700.0))]
    assert build_tls_flow_ranking(net_path, {"10": 900.0, "12": 1800.0}, exclude={"2"}) == []


def test_webster_plan_splits() -> None:
    plan = webster_plan([0.5, 0.25], 16.0)
    assert plan.cycle_s == pytest.approx(116.0, abs=0.1)
    assert plan.greens_s == pytest.approx((66.7, 33.3), abs=0.2)


def test_webster_plan_oversaturated_clamps() -> None:
    plan = webster_plan([0.6, 0.5], 16.0)
    assert plan.cycle_s == pytest.approx(120.0)
    assert sum(plan.greens_s) + plan.lost_time_s == pytest.approx(plan.cycle_s)
    assert min(plan.greens_s) >= 8.0


def test_plan_with_cycle_rejects_short_cycle() -> None:
    with pytest.raises(ValueError, match="cycle too short"):
        plan_with_cycle([0.5, 0.25], 16.0, 20.0)


def test_retime_program_preserves_yellows() -> None:
    phases = [
        {"duration": 39, "state": "GGGrr"},
        {"duration": 6, "state": "yyyrr"},
        {"duration": 39, "state": "rrrGG"},
        {"duration": 6, "state": "rrryy"},
    ]
    updated = retime_program(phases, [0, 2], [50.0, 40.0])
    assert [phase["duration"] for phase in updated] == [50.0, 6, 40.0, 6]
    assert updated[1]["state"] == "yyyrr"


def test_programs_roundtrip_and_apply(mini_net: tuple[Path, dict], tmp_path: Path) -> None:
    net_path, _ = mini_net
    table = build_tls_flow_table(net_path, {"10": 900.0, "12": 1800.0}, window_hours=1.0)
    programs = programs_from_table(table, ["2"], {"2": (50.0, 30.0)})
    path = save_signal_file(
        tmp_path / "signals.json",
        area="mini-sim",
        algorithm="webster+test",
        cycle_s=92.0,
        programs=programs,
        offsets={"2": 12.0},
    )
    loaded = load_signal_file(path)
    assert loaded["offsets"] == {"2": 12.0}
    assert loaded["programs"]["2"][0]["duration"] == 50.0
    applied = apply_programs_to_net(
        net_path, loaded["programs"], tmp_path / "net.xml", offsets=loaded["offsets"]
    )
    root = ET.parse(applied).getroot()
    logic = next(item for item in root.findall("tlLogic") if item.get("id") == "2")
    assert logic.get("offset") == "12.0"
    assert [phase.get("duration") for phase in logic.findall("phase")] == [
        "50.0",
        "6.0",
        "30.0",
        "6.0",
    ]


def test_apply_programs_rejects_missing_junction(
    mini_net: tuple[Path, dict], tmp_path: Path
) -> None:
    net_path, _ = mini_net
    with pytest.raises(ValueError, match="not found"):
        apply_programs_to_net(net_path, {"nope": []}, tmp_path / "net.xml")
