# Raw data

This directory holds **reconnaissance summaries only**. Raw downloads are cached
under `data/cache/` and are never committed.

| File | Source | License | Regenerate with |
|---|---|---|---|
| `recon_san-ysidro.json` | OpenStreetMap via Overpass API | ODbL | `uv run python scripts/recon_overpass.py` |

## Planned sources (fetch scripts land with the demand module)

- **BTS Border Crossing/Entry Data** — monthly inbound vehicle volumes for the
  San Ysidro port (`data.transportation.gov`, Socrata API). Public domain.
- **CBP Border Wait Times** — live and historical wait times by lane type
  (`bwt.cbp.gov`). Public.
- **TomTom Traffic Index** — city-level congestion context for reports. Citation only.

Attribution requirements: OSM data must credit "© OpenStreetMap contributors"
in derived reports.
