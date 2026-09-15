"""Download and cache the OSM drive network for a study area."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import osmnx as ox

from rushlab.config import Area

DEFAULT_CACHE_ROOT = Path("data/cache/areas")
ATTRIBUTION = "(c) OpenStreetMap contributors (ODbL)"


def area_cache_dir(area_name: str, cache_root: Path = DEFAULT_CACHE_ROOT) -> Path:
    return cache_root / area_name


def fetch_area(area: Area, *, refresh: bool = False, cache_root: Path = DEFAULT_CACHE_ROOT) -> Path:
    """Return the cached GraphML path, downloading via Overpass when needed.

    osmnx HTTP response caching is redirected to ``<cache_root>/../osmnx`` so no
    stray ``cache/`` directory appears in the repo root.
    """
    cache_dir = area_cache_dir(area.name, cache_root)
    graphml = cache_dir / "graph.graphml"
    meta_path = cache_dir / "meta.json"
    if graphml.is_file() and not refresh:
        return graphml

    ox.settings.use_cache = True
    ox.settings.cache_folder = str(cache_root.parent / "osmnx")
    graph = ox.graph_from_bbox(area.osmnx_bbox(), network_type="drive")
    cache_dir.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, graphml)
    meta = {
        "area": area.name,
        "bbox": list(area.bbox),
        "osmnx_bbox": list(area.osmnx_bbox()),
        "network_type": "drive",
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "source": "OpenStreetMap via Overpass API",
        "license": "ODbL",
        "attribution": ATTRIBUTION,
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    return graphml
