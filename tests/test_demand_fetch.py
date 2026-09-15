"""Live BTS/CBP integration test. Excluded from CI via the integration marker."""

from __future__ import annotations

from pathlib import Path

import pytest

from rushlab.config import get_area
from rushlab.demand.bts import load_volumes, trailing_daily_average
from rushlab.demand.cbp import fetch_snapshot


@pytest.mark.integration
def test_live_demand_sources(tmp_path: Path) -> None:
    area = get_area("san-ysidro")
    frame = load_volumes(area, refresh=True, cache_root=tmp_path)
    assert trailing_daily_average(frame) > 0
    snapshot = fetch_snapshot(area, refresh=True, cache_root=tmp_path)
    assert snapshot["pov"]["max_lanes"] and snapshot["pov"]["max_lanes"] > 0
