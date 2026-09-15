"""Live Overpass integration test. Excluded from CI via the integration marker."""

from __future__ import annotations

from pathlib import Path

import pytest

from rushlab.config import get_area
from rushlab.network.fetch import fetch_area


@pytest.mark.integration
def test_fetch_area_downloads_and_caches(tmp_path: Path) -> None:
    area = get_area("san-ysidro")
    graphml = fetch_area(area, cache_root=tmp_path)
    assert graphml.is_file()
    assert (tmp_path / area.name / "meta.json").is_file()
    assert fetch_area(area, cache_root=tmp_path) == graphml
