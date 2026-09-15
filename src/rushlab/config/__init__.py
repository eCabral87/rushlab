"""Study-area registry loaded from areas.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).parent / "areas.yaml"

BBox = tuple[float, float, float, float]
Coordinate = tuple[float, float]


@dataclass(frozen=True)
class BorderConfig:
    """Border-crossing metadata used to attach the synthetic sink."""

    name: str
    crossing_points: tuple[Coordinate, ...]
    sink_capacity_veh_h: float
    lane_types: tuple[str, ...] = ()
    bts_port_code: str = ""
    cbp_port_number: str = ""


@dataclass(frozen=True)
class Terminal:
    """Named gateway used as a source in capacity analysis."""

    name: str
    coordinates: Coordinate


@dataclass(frozen=True)
class Area:
    name: str
    description: str
    bbox: BBox  # (south, west, north, east)
    sim_bbox: BBox | None = None
    border: BorderConfig | None = None
    terminals: tuple[Terminal, ...] = ()

    def osmnx_bbox(self) -> tuple[float, float, float, float]:
        """osmnx expects (left, bottom, right, top) == (west, south, east, north)."""
        south, west, north, east = self.bbox
        return (west, south, east, north)


def _validate_bbox(name: str, value: object) -> BBox:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError(f"area {name!r}: bbox must be [south, west, north, east]")
    south, west, north, east = (float(component) for component in value)
    if not south < north:
        raise ValueError(f"area {name!r}: south must be < north")
    if not west < east:
        raise ValueError(f"area {name!r}: west must be < east")
    return (south, west, north, east)


def _parse_coordinate(name: str, value: object, field: str) -> Coordinate:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"area {name!r}: {field} must be [latitude, longitude]")
    return (float(value[0]), float(value[1]))


def _parse_border(name: str, raw: dict) -> BorderConfig:
    return BorderConfig(
        name=str(raw["name"]),
        crossing_points=tuple(
            _parse_coordinate(name, point, "crossing_points") for point in raw["crossing_points"]
        ),
        sink_capacity_veh_h=float(raw["sink_capacity_veh_h"]),
        lane_types=tuple(str(lane) for lane in raw.get("lane_types", ())),
        bts_port_code=str(raw.get("bts_port_code", "")),
        cbp_port_number=str(raw.get("cbp_port_number", "")),
    )


def _parse_area(name: str, raw: dict) -> Area:
    border_raw = raw.get("border")
    sim_bbox_raw = raw.get("sim_bbox")
    return Area(
        name=name,
        description=str(raw.get("description", "")),
        bbox=_validate_bbox(name, raw["bbox"]),
        sim_bbox=_validate_bbox(name, sim_bbox_raw) if sim_bbox_raw else None,
        border=_parse_border(name, border_raw) if border_raw else None,
        terminals=tuple(
            Terminal(
                name=str(terminal["name"]),
                coordinates=_parse_coordinate(name, terminal["coordinates"], "terminals"),
            )
            for terminal in raw.get("terminals", ())
        ),
    )


def load_areas(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Area]:
    data = yaml.safe_load(path.read_text()) or {}
    areas_raw = data.get("areas") or {}
    return {name: _parse_area(name, raw or {}) for name, raw in areas_raw.items()}


def get_area(name: str, path: Path = DEFAULT_CONFIG_PATH) -> Area:
    areas = load_areas(path)
    try:
        return areas[name]
    except KeyError:
        available = ", ".join(sorted(areas)) or "none"
        raise KeyError(f"unknown area {name!r}; available: {available}") from None
