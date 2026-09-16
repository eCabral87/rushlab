"""Baseline SUMO runs and KPI extraction."""

from __future__ import annotations

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from rushlab.config import Area
from rushlab.demand.calibration import load_calibration
from rushlab.signals.programs import load_signal_file
from rushlab.sim.demand import (
    DEFAULT_DEMAND_FACTOR,
    DEFAULT_WINDOW,
    destination_edge,
    gateway_edges,
    plan_trips,
    route_trips,
    write_trips_xml,
)
from rushlab.sim.metering import (
    apply_program_to_net,
    apply_programs_to_net,
    find_metering_target,
    metering_program,
    program_summary,
    write_tllogic_file,
)
from rushlab.sim.network import DEFAULT_CACHE_ROOT, build_sumo_network, read_net

DEFAULT_DERIVED_ROOT = Path("data/derived")
DEFAULT_RESULTS_ROOT = Path("results")


def prepare_baseline(
    area: Area,
    calibration: dict[str, Any],
    *,
    window: tuple[int, int] = DEFAULT_WINDOW,
    seed: int = 42,
    demand_factor: float = DEFAULT_DEMAND_FACTOR,
    refresh: bool = False,
    cache_root: Path = DEFAULT_CACHE_ROOT,
) -> dict[str, Any]:
    """Build network, apply port metering, generate and route demand."""
    if area.sim_bbox is None or area.border is None:
        raise ValueError(f"area {area.name!r} needs sim_bbox and border metadata")
    cache_dir = cache_root / area.name

    net_path, stats = build_sumo_network(area, refresh=refresh, cache_root=cache_root)
    net = read_net(net_path)
    crossing = area.border.crossing_points[0]
    destination = destination_edge(net, crossing)

    metering: dict[str, Any] | None = None
    forced_tls: str | None = None
    tls_set: tuple[str, ...] = ()
    target = find_metering_target(net_path, destination)
    if target is None:
        destination_node = net.getEdge(destination).getFromNode().getID()
        tls_set = (destination_node,)
        net_path, stats = build_sumo_network(area, cache_root=cache_root, tls_set=tls_set)
        net = read_net(net_path)
        target = find_metering_target(net_path, destination, max_hops=1)
        forced_tls = destination_node

    target_capacity = float(calibration["capacity_veh_h"]["central"])
    if target is not None:
        program = metering_program(
            target.phases, target.link_indices, target_capacity, target.lanes_to_port
        )
        if program:
            write_tllogic_file(cache_dir / "meter.tll.xml", target, program)
            metered_net = apply_program_to_net(
                net_path, target.junction_id, program, cache_dir / "sim-metered.net.xml"
            )
            net_path = metered_net
            net = read_net(net_path)
            metering = {
                "junction": target.junction_id,
                "link_indices": list(target.link_indices),
                "lanes_to_port": target.lanes_to_port,
                "target_capacity_veh_h": target_capacity,
                "forced_tls": forced_tls,
                **program_summary(program, target.link_indices, target.lanes_to_port),
            }

    gateways = gateway_edges(net, area.sim_bbox, crossing, destination=destination)
    plan = plan_trips(
        gateways,
        destination,
        calibration,
        window=window,
        seed=seed,
        demand_factor=demand_factor,
    )
    trips_path = write_trips_xml(plan["trips"], cache_dir / "baseline.trips.xml")
    routes_path = cache_dir / "baseline.rou.xml"
    routed = route_trips(trips_path, net_path, routes_path, seed=seed)

    port_queue_edges = [destination]
    if target is not None:
        port_queue_edges = [*target.approach_edges, destination]

    return {
        "net": net_path,
        "routes": routes_path,
        "destination": destination,
        "port_queue_edges": port_queue_edges,
        "gateways": gateways,
        "plan": {key: value for key, value in plan.items() if key != "trips"},
        "routed": routed,
        "network": stats,
        "metering": metering,
    }


EDGEDATA_PERIOD_S = 300


def write_sumocfg(
    directory: Path,
    net_path: Path,
    routes_path: Path,
    *,
    begin: int,
    end: int,
    seed: int,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    additional_path = directory / "portstats.add.xml"
    additional_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<additional>\n"
        f'  <edgeData id="portstats" file="edgedata.xml" period="{EDGEDATA_PERIOD_S}" '
        'excludeEmpty="false"/>\n'
        "</additional>\n"
    )
    configuration = ET.Element("configuration")
    inputs = ET.SubElement(configuration, "input")
    ET.SubElement(inputs, "net-file", value=str(net_path.resolve()))
    ET.SubElement(inputs, "route-files", value=str(routes_path.resolve()))
    ET.SubElement(inputs, "additional-files", value=str(additional_path.resolve()))
    time = ET.SubElement(configuration, "time")
    ET.SubElement(time, "begin", value=str(begin))
    ET.SubElement(time, "end", value=str(end))
    outputs = ET.SubElement(configuration, "output")
    ET.SubElement(outputs, "tripinfo-output", value="tripinfo.xml")
    ET.SubElement(outputs, "summary-output", value="summary.xml")
    report = ET.SubElement(configuration, "report")
    ET.SubElement(report, "no-step-log", value="true")
    ET.SubElement(report, "duration-log.statistics", value="true")
    processing = ET.SubElement(configuration, "processing")
    ET.SubElement(processing, "time-to-teleport", value="900")
    ET.SubElement(processing, "ignore-junction-blocker", value="60")
    ET.SubElement(configuration, "seed", value=str(seed))
    config_path = directory / "baseline.sumocfg"
    ET.ElementTree(configuration).write(config_path, encoding="utf-8", xml_declaration=True)
    return config_path


def run_sumo(config_path: Path, directory: Path) -> None:
    result = subprocess.run(
        ["sumo", "-c", str(config_path.resolve())],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    (directory / "sumo.log").write_text(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"sumo failed:\n{result.stderr[-2000:]}")


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 1) if values else None


def parse_metrics(directory: Path, port_edges: list[str]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    summary_path = directory / "summary.xml"
    if summary_path.is_file():
        steps = ET.parse(summary_path).getroot().findall("step")
        if steps:
            last = steps[-1]
            metrics.update(
                {
                    "inserted": int(last.get("inserted", 0)),
                    "arrived": int(last.get("arrived", 0)),
                    "running": int(last.get("running", 0)),
                    "teleports": int(last.get("teleports", 0)),
                    "mean_speed_kph": round(float(last.get("meanSpeed", 0)) * 3.6, 1),
                    "mean_travel_time_s": round(float(last.get("meanTravelTime", 0)), 1),
                }
            )
    tripinfo_path = directory / "tripinfo.xml"
    if tripinfo_path.is_file():
        trips = ET.parse(tripinfo_path).getroot().findall("tripinfo")
        metrics["completed_trips"] = len(trips)
        metrics["mean_trip_duration_s"] = _mean([float(trip.get("duration", 0)) for trip in trips])
        metrics["mean_trip_time_loss_s"] = _mean([float(trip.get("timeLoss", 0)) for trip in trips])
    edgedata_path = directory / "edgedata.xml"
    if edgedata_path.is_file() and port_edges:
        destination = port_edges[-1]
        approach = set(port_edges[:-1])
        arrived_total = 0.0
        throughput_samples: list[float] = []
        approach_waiting = 0.0
        approach_speeds: list[float] = []
        sim_begin: float | None = None
        sim_end: float | None = None
        for interval in ET.parse(edgedata_path).getroot().findall("interval"):
            begin = float(interval.get("begin", 0))
            end = float(interval.get("end", 0))
            sim_begin = begin if sim_begin is None else min(sim_begin, begin)
            sim_end = end if sim_end is None else max(sim_end, end)
            duration = end - begin
            for edge in interval.findall("edge"):
                edge_id = edge.get("id")
                if edge_id == destination:
                    arrived = float(edge.get("arrived", 0))
                    arrived_total += arrived
                    if duration > 0:
                        throughput_samples.append(arrived * 3600 / duration)
                if edge_id in approach:
                    approach_waiting += float(edge.get("waitingTime", 0))
                    speed = float(edge.get("speed", 0))
                    if speed > 0:
                        approach_speeds.append(speed)
        if sim_end is not None and sim_begin is not None and sim_end > sim_begin:
            metrics["port_throughput_veh_h"] = round(
                arrived_total * 3600 / (sim_end - sim_begin), 1
            )
        if throughput_samples:
            metrics["port_throughput_peak_veh_h"] = round(max(throughput_samples), 1)
        metrics["port_approach_waiting_time_s"] = round(approach_waiting, 1)
        if approach_speeds:
            metrics["port_approach_min_speed_kph"] = round(min(approach_speeds) * 3.6, 2)
    return metrics


def run_scenario(
    area: Area,
    *,
    scenario: str = "baseline",
    window: tuple[int, int] = DEFAULT_WINDOW,
    seed: int = 42,
    demand_factor: float = DEFAULT_DEMAND_FACTOR,
    signals_path: Path | None = None,
    refresh: bool = False,
    cache_root: Path = DEFAULT_CACHE_ROOT,
    derived_root: Path = DEFAULT_DERIVED_ROOT,
    results_root: Path = DEFAULT_RESULTS_ROOT,
) -> dict[str, Any]:
    calibration = load_calibration(derived_root / area.name / "calibration.json")
    if calibration is None:
        raise RuntimeError(f"no calibration for {area.name}; run: rushlab demand {area.name}")

    prepared = prepare_baseline(
        area,
        calibration,
        window=window,
        seed=seed,
        demand_factor=demand_factor,
        refresh=refresh,
        cache_root=cache_root,
    )

    signals_meta: dict[str, Any] | None = None
    if signals_path is not None:
        signal_file = load_signal_file(signals_path)
        applied_net = signals_path.with_name(f"{signals_path.stem}.net.xml")
        net_path = apply_programs_to_net(
            prepared["net"],
            signal_file["programs"],
            applied_net,
            offsets=signal_file.get("offsets", {}),
        )
        signals_meta = {
            "path": str(signals_path),
            "algorithm": signal_file.get("algorithm"),
            "junctions": sorted(signal_file["programs"]),
            "cycle_s": signal_file.get("cycle_s"),
        }
        prepared = {**prepared, "net": net_path}
    output_dir = results_root / area.name / "sumo" / scenario
    config_path = write_sumocfg(
        output_dir,
        prepared["net"],
        prepared["routes"],
        begin=window[0] * 3600,
        end=window[1] * 3600,
        seed=seed,
    )
    run_sumo(config_path, output_dir)
    metrics = parse_metrics(output_dir, prepared["port_queue_edges"])
    summary = {
        "area": area.name,
        "scenario": scenario,
        "window": f"{window[0]:02d}:00-{window[1]:02d}:00",
        "seed": seed,
        "network": prepared["network"],
        "destination_edge": prepared["destination"],
        "port_queue_edges": prepared["port_queue_edges"],
        "gateways": prepared["gateways"],
        "plan": prepared["plan"],
        "routed": prepared["routed"],
        "metering": prepared["metering"],
        "signals": signals_meta,
        "metrics": metrics,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    )
    return summary
