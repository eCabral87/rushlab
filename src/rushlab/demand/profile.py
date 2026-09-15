"""Documented northbound demand profile (assumption, refinable from snapshots)."""

from __future__ import annotations

PEAK_WINDOW = (6, 10)
PROFILE_NAME = "northbound-commuter"
PROFILE_SOURCE = (
    "Documented commuter profile: shape informed by CBP morning wait-time peaks "
    "(San Ysidro general lanes) and typical cross-border commuting patterns; to be "
    "refined from committed CBP snapshots as they accumulate."
)

# Relative hourly weights for northbound personal vehicles; normalized on use.
PROFILE_WEIGHTS: dict[int, float] = {
    0: 10.0,
    1: 6.0,
    2: 4.0,
    3: 4.0,
    4: 18.0,
    5: 55.0,
    6: 95.0,
    7: 105.0,
    8: 90.0,
    9: 70.0,
    10: 55.0,
    11: 50.0,
    12: 50.0,
    13: 48.0,
    14: 48.0,
    15: 52.0,
    16: 58.0,
    17: 62.0,
    18: 58.0,
    19: 48.0,
    20: 40.0,
    21: 30.0,
    22: 20.0,
    23: 13.0,
}


def normalized_profile() -> dict[int, float]:
    total = sum(PROFILE_WEIGHTS.values())
    return {hour: weight / total for hour, weight in PROFILE_WEIGHTS.items()}


def peak_share(
    profile: dict[int, float] | None = None, window: tuple[int, int] = PEAK_WINDOW
) -> float:
    profile = profile or normalized_profile()
    start, end = window
    return sum(fraction for hour, fraction in profile.items() if start <= hour < end)


def hourly_demand(daily_total: float, profile: dict[int, float] | None = None) -> dict[int, float]:
    profile = profile or normalized_profile()
    return {hour: daily_total * fraction for hour, fraction in profile.items()}


def peak_hour_demand(daily_total: float, profile: dict[int, float] | None = None) -> float:
    """Arrival rate (veh/h) of the busiest hour under the profile."""
    hourly = hourly_demand(daily_total, profile)
    return max(hourly.values())
