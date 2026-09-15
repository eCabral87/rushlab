#!/usr/bin/env python3
"""Reproduce OSM reconnaissance counts for a study-area bounding box.

Usage:
    uv run python scripts/recon_overpass.py
    uv run python scripts/recon_overpass.py --bbox "32.525,-117.06,32.555,-116.97" --name san-ysidro
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "RushLab-recon/0.1 (research; github.com/eCabral87/rushlab)"
DEFAULT_BBOX = "32.525,-117.06,32.555,-116.97"
DEFAULT_NAME = "san-ysidro"
OUT_DIR = Path("data/raw")


def overpass_count(bbox: str, selector: str) -> int:
    """Return the total count of elements matching selector inside bbox."""
    south, west, north, east = (float(value) for value in bbox.split(","))
    query = f"[out:json][timeout:60];{selector}({south},{west},{north},{east});out count;"
    response = httpx.post(
        OVERPASS_URL,
        data={"data": query},
        headers={"User-Agent": USER_AGENT},
        timeout=90.0,
    )
    response.raise_for_status()
    elements = response.json()["elements"]
    return int(elements[0]["tags"]["total"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bbox", default=DEFAULT_BBOX, help="south,west,north,east")
    parser.add_argument("--name", default=DEFAULT_NAME, help="area name for the output file")
    args = parser.parse_args()

    report = {
        "area": args.name,
        "bbox": args.bbox,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": "OpenStreetMap via Overpass API",
        "license": "ODbL",
        "highway_ways": overpass_count(args.bbox, 'way["highway"]'),
        "traffic_signal_nodes": overpass_count(args.bbox, 'node["highway"="traffic_signals"]'),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"recon_{args.name}.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
