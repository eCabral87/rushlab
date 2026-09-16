"""Webster cycle length and green-split computation."""

from __future__ import annotations

from dataclasses import dataclass

MAX_FLOW_RATIO = 0.95


@dataclass(frozen=True)
class WebsterPlan:
    cycle_s: float
    greens_s: tuple[float, ...]
    y_total: float
    lost_time_s: float


def _allocate_greens(ratios: list[float], green_total: float, min_green_s: float) -> list[float]:
    """Proportional allocation with minimum greens; greedy freeze-and-reduce."""
    count = len(ratios)
    greens = [0.0] * count
    free = list(range(count))
    remaining = green_total
    while free:
        ratio_sum = sum(ratios[index] for index in free)
        if ratio_sum > 0:
            shares = {index: ratios[index] / ratio_sum for index in free}
        else:
            shares = {index: 1.0 / len(free) for index in free}
        violated = [index for index in free if remaining * shares[index] < min_green_s]
        if not violated:
            for index in free:
                greens[index] = remaining * shares[index]
            break
        for index in violated:
            greens[index] = min_green_s
            remaining -= min_green_s
        free = [index for index in free if index not in violated]
        if remaining <= 0:
            break
    return greens


def webster_plan(
    ratios: list[float],
    lost_time_s: float,
    *,
    min_cycle_s: float = 30.0,
    max_cycle_s: float = 120.0,
    min_green_s: float = 8.0,
) -> WebsterPlan:
    """Classic Webster plan: C0 = (1.5 L + 5) / (1 - Y), splits proportional to y."""
    if not ratios:
        raise ValueError("at least one phase ratio is required")
    y_total = sum(ratios)
    if y_total <= 0:
        cycle = min_cycle_s
    else:
        y_effective = min(y_total, MAX_FLOW_RATIO)
        cycle = (1.5 * lost_time_s + 5.0) / (1.0 - y_effective)
    floor_cycle = lost_time_s + min_green_s * len(ratios)
    cycle = min(max(cycle, min_cycle_s, floor_cycle), max(max_cycle_s, floor_cycle))
    greens = _allocate_greens(ratios, cycle - lost_time_s, min_green_s)
    return WebsterPlan(
        cycle_s=sum(greens) + lost_time_s,
        greens_s=tuple(greens),
        y_total=y_total,
        lost_time_s=lost_time_s,
    )


def plan_with_cycle(
    ratios: list[float],
    lost_time_s: float,
    cycle_s: float,
    *,
    min_green_s: float = 8.0,
) -> WebsterPlan:
    """Recompute splits for a fixed (common corridor) cycle."""
    if cycle_s <= lost_time_s + min_green_s * len(ratios):
        raise ValueError("cycle too short for the lost time and minimum greens")
    greens = _allocate_greens(ratios, cycle_s - lost_time_s, min_green_s)
    return WebsterPlan(
        cycle_s=cycle_s,
        greens_s=tuple(greens),
        y_total=sum(ratios),
        lost_time_s=lost_time_s,
    )


def retime_program(
    phases: list[dict], green_positions: list[int], greens: list[float]
) -> list[dict]:
    """Apply new green durations, leaving yellow/clearance phases untouched."""
    if len(green_positions) != len(greens):
        raise ValueError("green positions and greens length mismatch")
    updated: list[dict] = []
    for position, phase in enumerate(phases):
        duration = float(phase["duration"])
        if position in green_positions:
            duration = greens[green_positions.index(position)]
        updated.append(
            {
                "duration": round(duration, 1),
                "state": str(phase["state"]),
                "name": str(phase.get("name", "")),
            }
        )
    return updated
