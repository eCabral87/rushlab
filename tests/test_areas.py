"""Study-area registry tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from rushlab.config import Area, get_area, load_areas


def test_load_areas_includes_san_ysidro() -> None:
    area = load_areas()["san-ysidro"]
    assert isinstance(area, Area)
    assert area.bbox == (32.525, -117.06, 32.555, -116.97)
    assert area.sim_bbox is not None
    assert area.sim_bbox[0] > area.bbox[0]  # sim window is tighter


def test_border_metadata_parsed() -> None:
    border = get_area("san-ysidro").border
    assert border is not None
    assert border.sink_capacity_veh_h > 0
    assert border.lane_types == ("general", "ready", "sentri")
    assert border.crossing_points


def test_terminals_parsed() -> None:
    terminals = get_area("san-ysidro").terminals
    assert {terminal.name for terminal in terminals} == {"via-rapida-west", "padre-kino-centro"}


def test_osmnx_bbox_conversion() -> None:
    assert get_area("san-ysidro").osmnx_bbox() == (-117.06, 32.525, -116.97, 32.555)


def test_unknown_area_lists_available() -> None:
    with pytest.raises(KeyError, match="san-ysidro"):
        get_area("does-not-exist")


def test_invalid_bbox_rejected(tmp_path: Path) -> None:
    config = {"areas": {"bad": {"description": "", "bbox": [32.6, -117.0, 32.5, -116.9]}}}
    path = tmp_path / "areas.yaml"
    path.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="south must be < north"):
        load_areas(path)
