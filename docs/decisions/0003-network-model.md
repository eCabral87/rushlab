# 0003 — Network model and analytic assumptions

- Status: accepted
- Date: 2026-09-15

## Context

The analytic layer must turn an OSM extract into a graph that supports bottleneck
analysis, capacity cuts, and (later) SUMO export, without pretending to be a
calibrated traffic model yet. Data quality in Tijuana is uneven: `maxspeed` and
`lanes` tags are frequently missing, and turn restrictions are unreliable.

## Decisions

1. **Ingestion:** `osmnx.graph_from_bbox(..., network_type="drive")` via Overpass,
   cached as GraphML under `data/cache/areas/<name>/` (never committed). The
   bbox comes from `src/rushlab/config/areas.yaml`; `sim_bbox` is reserved for
   the D4 microsimulation window.
2. **Analytic graph:** a `networkx.DiGraph` where parallel edges collapse to the
   fastest one (by travel time). This keeps one representative link per street
   direction and is deterministic for ranking purposes.
3. **Travel time:** `length / speed`; speed is the parsed `maxspeed` when
   available, otherwise a highway-class fallback table (`DEFAULT_SPEEDS`,
   conservative urban values). This is a free-flow proxy — no congestion.
4. **Capacity proxy:** `lanes x 1800 veh/h`, with lane defaults by class
   (`DEFAULT_LANES`) when `lanes` is untagged. This is a structural proxy for
   min-cut analysis, not an operational capacity.
5. **Border sink:** a synthetic `border_sink` node connects to the road nodes
   nearest each crossing point (600 m search radius). Connector delay is a
   placeholder 30 s; sink throughput comes from `areas.yaml` as a placeholder
   until D4 calibration against BTS volumes and CBP wait times.
6. **Orientation:** the graph keeps both directions; the northbound perspective
   is expressed through `travel_time_to_sink` (shortest paths on the reversed
   graph) rather than by deleting southbound edges.
7. **Volatility metrics:** articulation points and bridges are computed on the
   undirected view (standard definition). Betweenness uses travel time as weight
   and switches to seeded sampling (`k=500`) above 5,000 nodes for runtime.

## Baseline results (2026-09-15, OSM extract)

| Metric | Value |
|---|---|
| Nodes / edges (analytic) | 2,302 / 5,665 |
| Signalized intersections | 130 |
| Weak components | 1 (largest = 100%) |
| Articulation points / bridges | 333 / 361 |
| Nodes able to reach the sink | 98.5% |
| Median travel time to sink | 308 s |
| Min cut to sink (placeholder capacity) | via-rapida-west 4,800 veh/h; padre-kino-centro 1,800 veh/h |
| Top bottleneck | Calzada Defensores de Baja California / Blvd Cuauhtémoc Norte |

## Consequences

- Absolute values are structural approximations; only comparisons between
  scenarios run with identical assumptions are meaningful.
- The capacity proxy and sink placeholders must be replaced in D4 before any
  claim about intervention effects.
- The study bbox spans beyond the immediate approach (results are dominated by
  central Tijuana arteries); the tighter `sim_bbox` scopes microsimulation work.
- Adding an area is a documented skill procedure (`add-study-area`) with the
  same assumptions recorded per area.
