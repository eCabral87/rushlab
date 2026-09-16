"""SUMO network construction from OpenStreetMap XML."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import sumolib

from rushlab.config import Area

OVERPASS_ENDPOINTS: tuple[str, ...] = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
USER_AGENT = "RushLab/0.1 (github.com/eCabral87/rushlab)"
DEFAULT_CACHE_ROOT = Path("data/cache/sumo")
NETCONVERT_OPTIONS: tuple[str, ...] = (
    "--geometry.remove",
    "true",
    "--ramps.guess",
    "true",
    "--junctions.join",
    "true",
    "--tls.guess-signals",
    "true",
    "--tls.discard-simple",
    "true",
    "--no-turnarounds",
    "true",
    "--output.street-names",
    "true",
)


MAIN_ROAD_FILTER = '["highway"~"^(motorway|trunk|primary|secondary|tertiary)(_link)?$"]'


def osm_xml_query(bbox: tuple[float, float, float, float]) -> str:
    south, west, north, east = bbox
    return (
        f"[out:xml][timeout:180];(way{MAIN_ROAD_FILTER}"
        f"({south},{west},{north},{east});>;);out body;"
    )


def fetch_osm_xml(
    area: Area, *, refresh: bool = False, cache_root: Path = DEFAULT_CACHE_ROOT
) -> Path:
    """Return the cached OSM XML path for the simulation bbox, downloading if needed."""
    if area.sim_bbox is None:
        raise ValueError(f"area {area.name!r} has no sim_bbox; add it to areas.yaml")
    cache_dir = cache_root / area.name
    osm_path = cache_dir / "map.osm"
    meta_path = cache_dir / "meta.json"
    if osm_path.is_file() and not refresh:
        return osm_path

    response: httpx.Response | None = None
    last_error: Exception | None = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            candidate = httpx.post(
                endpoint,
                data={"data": osm_xml_query(area.sim_bbox)},
                headers={"User-Agent": USER_AGENT},
                timeout=300.0,
            )
            candidate.raise_for_status()
            response = candidate
            break
        except httpx.HTTPError as error:
            last_error = error
    if response is None:
        raise RuntimeError(
            f"Overpass XML export failed on all endpoints: {last_error}"
        ) from last_error
    cache_dir.mkdir(parents=True, exist_ok=True)
    osm_path.write_text(response.text)
    meta = {
        "area": area.name,
        "sim_bbox": list(area.sim_bbox),
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "bytes": len(response.text),
        "source": "OpenStreetMap via Overpass API (XML export)",
        "license": "ODbL",
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    return osm_path


def read_net(net_path: Path) -> sumolib.net.Net:
    return sumolib.net.readNet(str(net_path))


def build_sumo_network(
    area: Area,
    *,
    refresh: bool = False,
    cache_root: Path = DEFAULT_CACHE_ROOT,
    tllogic_files: Path | None = None,
    tls_set: tuple[str, ...] = (),
) -> tuple[Path, dict[str, Any]]:
    """Build (or reuse) the SUMO network and return its path plus stats."""
    if shutil.which("netconvert") is None:
        raise RuntimeError("netconvert not found on PATH; run inside the project environment")
    cache_dir = cache_root / area.name
    osm_path = fetch_osm_xml(area, refresh=refresh, cache_root=cache_root)
    net_path = cache_dir / "sim.net.xml"
    needs_build = refresh or not net_path.is_file() or tllogic_files is not None or bool(tls_set)
    if needs_build:
        command = [
            "netconvert",
            "--osm-files",
            str(osm_path),
            "--output-file",
            str(net_path),
            *NETCONVERT_OPTIONS,
        ]
        if tllogic_files is not None:
            command += ["--tllogic-files", str(tllogic_files)]
        if tls_set:
            command += ["--tls.set", ",".join(tls_set)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"netconvert failed:\n{result.stderr[-2000:]}")
    return net_path, network_stats(net_path)


def network_stats(net_path: Path) -> dict[str, Any]:
    net = read_net(net_path)
    nodes = net.getNodes()
    edges = net.getEdges(withInternal=False)
    traffic_lights = [node for node in nodes if node.getType() == "traffic_light"]
    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "traffic_lights": len(traffic_lights),
    }
