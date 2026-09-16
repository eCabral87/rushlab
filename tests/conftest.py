"""Shared fixtures for SUMO tests; no network access."""

from __future__ import annotations

from pathlib import Path

import pytest

from rushlab.config import Area, BorderConfig
from rushlab.sim.network import build_sumo_network

FIXTURE_OSM = Path(__file__).parent / "fixtures" / "mini.osm"
MINI_BBOX = (32.530, -117.045, 32.545, -117.015)
MINI_CROSSING = (32.5420, -117.0290)


@pytest.fixture()
def mini_area() -> Area:
    return Area(
        name="mini-sim",
        description="SUMO fixture area",
        bbox=MINI_BBOX,
        sim_bbox=MINI_BBOX,
        border=BorderConfig(
            name="Mini POE",
            crossing_points=(MINI_CROSSING,),
            sink_capacity_veh_h=4800.0,
            lane_types=("general",),
            bts_port_code="0",
            cbp_port_number="0",
        ),
    )


@pytest.fixture()
def mini_cache(tmp_path: Path, mini_area: Area) -> Path:
    cache_dir = tmp_path / "sumo" / mini_area.name
    cache_dir.mkdir(parents=True)
    (cache_dir / "map.osm").write_text(FIXTURE_OSM.read_text())
    return tmp_path / "sumo"


@pytest.fixture()
def mini_net(mini_area: Area, mini_cache: Path) -> tuple[Path, dict]:
    return build_sumo_network(mini_area, cache_root=mini_cache)
