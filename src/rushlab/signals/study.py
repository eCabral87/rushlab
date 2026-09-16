"""Signal optimization study orchestration."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rushlab.config import Area
from rushlab.demand.calibration import load_calibration
from rushlab.signals.evaluator import EvaluatorConfig
from rushlab.signals.flows import build_tls_flow_table, load_edge_flows
from rushlab.signals.optimizer import BUDGETS, optimize_offsets
from rushlab.signals.programs import (
    build_tls_flow_ranking,
    default_signal_path,
    programs_from_table,
    save_signal_file,
)
from rushlab.signals.webster import plan_with_cycle, webster_plan
from rushlab.sim.runner import (
    DEFAULT_CACHE_ROOT,
    DEFAULT_DERIVED_ROOT,
    DEFAULT_RESULTS_ROOT,
    prepare_baseline,
    run_scenario,
)

DEFAULT_TOP_K = 8
DEFAULT_WINDOW = (6, 10)
DEFAULT_EVAL_WINDOW = (6, 8)
DEFAULT_WORKERS = 4


def optimize_area_signals(
    area: Area,
    *,
    budget: str = "light",
    top_k: int = DEFAULT_TOP_K,
    window: tuple[int, int] = DEFAULT_WINDOW,
    eval_window: tuple[int, int] = DEFAULT_EVAL_WINDOW,
    seed: int = 42,
    workers: int = DEFAULT_WORKERS,
    cache_root: Path = DEFAULT_CACHE_ROOT,
    derived_root: Path = DEFAULT_DERIVED_ROOT,
    results_root: Path = DEFAULT_RESULTS_ROOT,
) -> dict[str, Any]:
    """Webster retiming + GA offset optimization on the busiest signals."""
    if budget not in BUDGETS:
        raise ValueError(f"unknown budget {budget!r}; choose from {sorted(BUDGETS)}")
    calibration = load_calibration(derived_root / area.name / "calibration.json")
    if calibration is None:
        raise RuntimeError(f"no calibration for {area.name}; run: rushlab demand {area.name}")

    baseline_edgedata = results_root / area.name / "sumo" / "baseline" / "edgedata.xml"
    if not baseline_edgedata.is_file():
        run_scenario(
            area,
            scenario="baseline",
            window=window,
            seed=seed,
            cache_root=cache_root,
            derived_root=derived_root,
            results_root=results_root,
        )

    prepared = prepare_baseline(area, calibration, window=window, seed=seed, cache_root=cache_root)
    net_path = prepared["net"]
    port_junction = (prepared["metering"] or {}).get("junction")

    edge_flows = load_edge_flows(baseline_edgedata)
    window_hours = float(window[1] - window[0])
    flow_table = build_tls_flow_table(net_path, edge_flows, window_hours=window_hours)
    ranking = build_tls_flow_ranking(
        net_path, edge_flows, exclude={str(port_junction)} if port_junction else None
    )
    selected = [junction for junction, _ in ranking if junction in flow_table][:top_k]
    if not selected:
        raise RuntimeError("no signals selected for optimization")

    base_plans = {
        junction: webster_plan(
            [float(ratio) for ratio in flow_table[junction]["ratios"]],
            float(flow_table[junction]["lost_time_s"]),
        )
        for junction in selected
    }
    common_cycle = max(plan.cycle_s for plan in base_plans.values())
    final_plans = {
        junction: plan_with_cycle(
            [float(ratio) for ratio in flow_table[junction]["ratios"]],
            float(flow_table[junction]["lost_time_s"]),
            common_cycle,
        )
        for junction in selected
    }
    greens = {junction: final_plans[junction].greens_s for junction in selected}
    programs = programs_from_table(flow_table, selected, greens)

    evaluator = EvaluatorConfig(
        net_path=net_path,
        routes_path=prepared["routes"],
        base_programs=programs,
        working_root=cache_root / area.name / "ga",
        begin_s=eval_window[0] * 3600,
        end_s=eval_window[1] * 3600,
        seed=seed,
    )
    cycles = {junction: common_cycle for junction in selected}
    result = optimize_offsets(
        evaluator, selected, cycles, budget=budget, seed=seed, workers=workers
    )

    signal_file = default_signal_path(cache_root, area.name, "optimized")
    save_signal_file(
        signal_file,
        area=area.name,
        algorithm=f"webster+ga-offsets({budget})",
        cycle_s=common_cycle,
        programs=programs,
        offsets=result.offsets,
        metadata={
            "selected_junctions": selected,
            "eval_window": f"{eval_window[0]:02d}:00-{eval_window[1]:02d}:00",
            "fitness": result.fitness,
            "evaluations": result.evaluations,
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        },
    )

    validation = run_scenario(
        area,
        scenario="optimized",
        window=window,
        seed=seed,
        signals_path=signal_file,
        cache_root=cache_root,
        derived_root=derived_root,
        results_root=results_root,
    )

    study = {
        "area": area.name,
        "algorithm": f"webster+ga-offsets({budget})",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "window": f"{window[0]:02d}:00-{window[1]:02d}:00",
        "eval_window": f"{eval_window[0]:02d}:00-{eval_window[1]:02d}:00",
        "seed": seed,
        "excluded_port_junction": port_junction,
        "ranking": [
            {"junction": junction, "approach_flow": flow} for junction, flow in ranking[:top_k]
        ],
        "selected": selected,
        "common_cycle_s": common_cycle,
        "plans": {
            junction: {
                "cycle_s": final_plans[junction].cycle_s,
                "greens_s": list(final_plans[junction].greens_s),
                "y_total": round(final_plans[junction].y_total, 3),
                "lost_time_s": final_plans[junction].lost_time_s,
            }
            for junction in selected
        },
        "ga": {
            "budget": budget,
            "evaluations": result.evaluations,
            "best_fitness": result.fitness,
            "history": result.history,
        },
        "offsets": result.offsets,
        "signal_file": str(signal_file),
        "validation": {
            "scenario": "optimized",
            "metrics": validation["metrics"],
        },
    }
    study_dir = results_root / area.name / "signals"
    study_dir.mkdir(parents=True, exist_ok=True)
    (study_dir / "optimization.json").write_text(
        json.dumps(study, indent=2, ensure_ascii=False) + "\n"
    )
    return study
