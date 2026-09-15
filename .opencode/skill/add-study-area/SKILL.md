---
name: add-study-area
description: Use when adding a new geographic study area or corridor to RushLab. Covers bbox selection, OSM reconnaissance, area config registration, network build validation, and tests. Trigger keywords: new area, corridor, bbox, study area, OSM extract.
---

# Add a Study Area

## Goal

Register a new geographic area so it can be fetched, built, simulated, and reported
on like the existing San Ysidro corridor.

## Procedure

1. **Pick the bbox.** Keep it as tight as possible around the corridor of interest.
   Record it as `south,west,north,east` in decimal degrees.

2. **Reconnaissance first — always.**
   ```bash
   uv run python scripts/recon_overpass.py --bbox "<south,west,north,east>" --name <area>
   ```
   This writes `data/raw/recon_<area>.json` with highway-way and traffic-signal
   counts. If signal count is 0, the area has no signalized intersections and is
   not suitable for signal studies.

3. **Register the area** in `src/rushlab/config/areas.yaml` with name, bbox,
   description, and lane/border metadata where applicable.

4. **Build the network** (once the network module exists):
   ```bash
   uv run rushlab build-area <area>
   ```
   Validate: connected graph, expected intersection count, no orphan components
   larger than 5% of nodes. Document any manual geometry fixes in the area's ADR.

5. **Add a smoke test** in `tests/` that builds the area's graph from a cached
   fixture — do not hit the network in tests.

6. **Update docs:** add the area to README's recon table and note assumptions
   (signal phasing unknown, lane counts from OSM tags, etc.) in
   `docs/decisions/`.

## Rules

- Never commit raw OSM downloads; only recon summaries under `data/raw/`.
- Every new area requires an assumptions note. Missing data (turn restrictions,
  phasing) must be listed, not silently defaulted.
- If the area spans an international border, model the crossing as a
  capacity-controlled sink; see `docs/decisions/0001-scope.md`.
