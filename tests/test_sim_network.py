"""SUMO network build tests on the committed mini.osm fixture."""

from __future__ import annotations

from pathlib import Path

import pytest

from rushlab.config import Area
from rushlab.sim.network import (
    DEFAULT_CACHE_ROOT,
    build_sumo_network,
    fetch_osm_xml,
    read_net,
)


def test_network_stats(mini_net: tuple[Path, dict]) -> None:
    net_path, stats = mini_net
    assert stats == {"nodes": 4, "edges": 4, "traffic_lights": 1}
    net = read_net(net_path)
    tls_nodes = [node for node in net.getNodes() if node.getType() == "traffic_light"]
    assert len(tls_nodes) == 1


def test_rebuild_is_cached(mini_area: Area, mini_cache: Path) -> None:
    first, _ = build_sumo_network(mini_area, cache_root=mini_cache)
    second, _ = build_sumo_network(mini_area, cache_root=mini_cache)
    assert first == second
    assert first.is_file()


def test_fetch_requires_sim_bbox(mini_area: Area) -> None:
    area = Area(
        name="no-bbox",
        description="",
        bbox=(32.53, -117.05, 32.55, -117.01),
        border=mini_area.border,
    )
    with pytest.raises(ValueError, match="sim_bbox"):
        fetch_osm_xml(area, cache_root=Path("/tmp/unused"))


def test_network_stats_default_path_exists() -> None:
    assert DEFAULT_CACHE_ROOT.name == "sumo"


@pytest.mark.integration
def test_fetch_osm_xml_live(tmp_path: Path) -> None:
    from rushlab.config import get_area

    path = fetch_osm_xml(get_area("san-ysidro"), refresh=True, cache_root=tmp_path)
    assert path.stat().st_size > 0
