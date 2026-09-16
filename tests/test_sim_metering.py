"""Port metering program tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from rushlab.sim.metering import (
    apply_program_to_net,
    find_metering_target,
    metering_program,
    program_summary,
    write_tllogic_file,
)


def test_find_target_upstream_of_port_edge(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    target = find_metering_target(net_path, "11")
    assert target is not None
    assert target.junction_id == "2"
    assert target.link_indices == (0, 3, 4)
    assert target.lanes_to_port == 3


def test_no_target_when_no_tls_upstream(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    assert find_metering_target(net_path, "12") is None


def test_metering_program_matches_target_capacity(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    target = find_metering_target(net_path, "11")
    assert target is not None
    program = metering_program(target.phases, target.link_indices, 1600.0, target.lanes_to_port)
    assert program is not None
    assert len(program) == len(target.phases)
    summary = program_summary(program, target.link_indices, target.lanes_to_port)
    assert summary["estimated_capacity_veh_h"] == pytest.approx(1600.0, rel=0.05)
    assert summary["cycle_s"] > 0


def test_target_above_natural_capacity_is_not_meterable(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    target = find_metering_target(net_path, "11")
    assert target is not None
    assert (
        metering_program(target.phases, target.link_indices, 2720.0, target.lanes_to_port) is None
    )


def test_metering_clamps_to_min_green(mini_net: tuple[Path, dict]) -> None:
    net_path, _ = mini_net
    target = find_metering_target(net_path, "11")
    assert target is not None
    program = metering_program(target.phases, target.link_indices, 50.0, target.lanes_to_port)
    assert program is not None
    port_durations = [
        float(phase["duration"])
        for phase in program
        if any(
            index < len(str(phase["state"])) and str(phase["state"])[index] == "G"
            for index in target.link_indices
        )
    ]
    assert min(port_durations) >= 8.0


def test_tllogic_file_roundtrip(mini_net: tuple[Path, dict], tmp_path: Path) -> None:
    import xml.etree.ElementTree as ET

    net_path, _ = mini_net
    target = find_metering_target(net_path, "11")
    assert target is not None
    program = metering_program(target.phases, target.link_indices, 1600.0, target.lanes_to_port)
    assert program is not None
    path = write_tllogic_file(tmp_path / "meter.tll.xml", target, program)
    root = ET.parse(path).getroot()
    logic = root.find("tlLogic")
    assert logic is not None
    assert logic.get("id") == "2"
    assert len(logic.findall("phase")) == len(program)


def test_apply_program_to_net(mini_net: tuple[Path, dict], tmp_path: Path) -> None:
    import xml.etree.ElementTree as ET

    net_path, _ = mini_net
    target = find_metering_target(net_path, "11")
    assert target is not None
    program = metering_program(target.phases, target.link_indices, 1600.0, target.lanes_to_port)
    assert program is not None
    out_path = apply_program_to_net(
        net_path, target.junction_id, program, tmp_path / "metered.net.xml"
    )
    root = ET.parse(out_path).getroot()
    logic = next(item for item in root.findall("tlLogic") if item.get("id") == "2")
    durations = [phase.get("duration") for phase in logic.findall("phase")]
    assert durations == [str(phase["duration"]) for phase in program]
