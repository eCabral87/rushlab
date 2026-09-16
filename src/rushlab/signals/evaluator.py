"""Candidate evaluation for signal optimization.

Each candidate patches the base network with its programs/offsets and runs
SUMO in a private directory. Offsets cannot be changed reliably at runtime in
SUMO 1.27, so patched nets are the exact and parallelizable route.
"""

from __future__ import annotations

import multiprocessing
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rushlab.sim.metering import apply_programs_to_net

TELEPORT_PENALTY_S = 600.0
ARRIVAL_BONUS_S = 20.0
DEFAULT_WORKERS = 4


@dataclass(frozen=True)
class EvaluatorConfig:
    net_path: Path
    routes_path: Path
    base_programs: dict[str, list[dict]]
    working_root: Path
    begin_s: int
    end_s: int
    seed: int
    teleport_penalty_s: float = TELEPORT_PENALTY_S
    arrival_bonus_s: float = ARRIVAL_BONUS_S


def _write_config(
    directory: Path, net_path: Path, routes_path: Path, config: EvaluatorConfig
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    configuration = ET.Element("configuration")
    inputs = ET.SubElement(configuration, "input")
    ET.SubElement(inputs, "net-file", value=str(net_path.resolve()))
    ET.SubElement(inputs, "route-files", value=str(routes_path.resolve()))
    time = ET.SubElement(configuration, "time")
    ET.SubElement(time, "begin", value=str(config.begin_s))
    ET.SubElement(time, "end", value=str(config.end_s))
    outputs = ET.SubElement(configuration, "output")
    ET.SubElement(outputs, "tripinfo-output", value="tripinfo.xml")
    ET.SubElement(outputs, "summary-output", value="summary.xml")
    report = ET.SubElement(configuration, "report")
    ET.SubElement(report, "no-step-log", value="true")
    processing = ET.SubElement(configuration, "processing")
    ET.SubElement(processing, "time-to-teleport", value="900")
    ET.SubElement(configuration, "seed", value=str(config.seed))
    config_path = directory / "candidate.sumocfg"
    ET.ElementTree(configuration).write(config_path, encoding="utf-8", xml_declaration=True)
    return config_path


def evaluate_candidate(config: EvaluatorConfig, offsets: dict[str, float]) -> dict[str, Any]:
    """Run one candidate and return its fitness and metrics."""
    directory = config.working_root / f"cand_{uuid.uuid4().hex[:12]}"
    net_path = apply_programs_to_net(
        config.net_path, config.base_programs, directory / "sim.net.xml", offsets=offsets
    )
    config_path = _write_config(directory, net_path, config.routes_path, config)
    result = subprocess.run(
        ["sumo", "-c", str(config_path.resolve())],
        cwd=directory,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"candidate sumo failed:\n{result.stderr[-1000:]}")
    metrics = _parse_candidate_outputs(directory)
    fitness = (
        metrics["total_time_loss_s"]
        + config.teleport_penalty_s * metrics["teleports"]
        - config.arrival_bonus_s * metrics["arrived"]
    )
    shutil.rmtree(directory, ignore_errors=True)
    return {
        "fitness": fitness,
        "offsets": offsets,
        "metrics": metrics,
    }


def _parse_candidate_outputs(directory: Path) -> dict[str, float]:
    metrics: dict[str, float] = {"teleports": 0.0, "arrived": 0.0, "total_time_loss_s": 0.0}
    summary_path = directory / "summary.xml"
    if summary_path.is_file():
        steps = ET.parse(summary_path).getroot().findall("step")
        if steps:
            last = steps[-1]
            metrics["teleports"] = float(last.get("teleports", 0))
            metrics["arrived"] = float(last.get("arrived", 0))
    tripinfo_path = directory / "tripinfo.xml"
    if tripinfo_path.is_file():
        trips = ET.parse(tripinfo_path).getroot().findall("tripinfo")
        metrics["total_time_loss_s"] = sum(float(trip.get("timeLoss", 0)) for trip in trips)
    return metrics


def _evaluate_job(payload: tuple[EvaluatorConfig, dict[str, float]]) -> dict[str, Any]:
    config, offsets = payload
    return evaluate_candidate(config, offsets)


def evaluate_many(
    config: EvaluatorConfig,
    candidates: list[dict[str, float]],
    *,
    workers: int = DEFAULT_WORKERS,
) -> list[dict[str, Any]]:
    """Evaluate candidates in parallel; order of results matches input order."""
    if workers <= 1 or len(candidates) == 1:
        return [evaluate_candidate(config, offsets) for offsets in candidates]
    jobs = [(config, offsets) for offsets in candidates]
    with multiprocessing.Pool(processes=workers) as pool:
        return pool.map(_evaluate_job, jobs)
