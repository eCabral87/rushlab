# 0005 — SUMO microsimulation model

- Status: accepted
- Date: 2026-09-15

## Context

D2 produced the analytic graph and D3 calibrated the border sink. D4 adds a
microsimulation that can test signal timing and lane-management scenarios. The
OSM network around the port is dense, the port queue dominates the corridor, and
no signal phasing data exists publicly.

## Decisions

1. **Simulation area:** `sim_bbox = [32.530, -117.050, 32.545, -117.008]` — the
   Mexico-side approach around El Chaparral with a short US-side stub.
2. **Network:** Overpass XML export filtered to main-road classes
   (`motorway|trunk|primary|secondary|tertiary` + `_link`), converted with
   `netconvert --tls.guess-signals --ramps.guess --junctions.join
   --no-turnarounds`. Result: **567 nodes, 952 edges, 48 traffic lights**.
   Residential/service streets are out of scope for v0.1.
3. **Port metering:** the port is modeled as a fixed-time signal metering the
   entry to the border crossing, with the green split derived from the calibrated
   central capacity (2,720 veh/h). When no traffic light exists upstream of the
   destination edge, one is forced with netconvert `--tls.set` and the generated
   net is patched in place — `--tllogic-files` cannot be combined with
   `--tls.set` in one netconvert run (load-order limitation).
4. **Demand:** boundary gateway edges whose direction heads toward the port,
   filtered to those that can topologically reach the destination edge;
   lane-weighted. Hourly demand = BTS trailing daily average x documented hourly
   profile x **demand factor 0.75** (share of port-bound traffic represented by
   modeled main-road gateways — an explicit approximation). Routing with
   `duarouter --seed 42`; unroutable trips are dropped and counted (~3%).
5. **Gridlock handling:** the baseline is deliberately oversaturated, so SUMO's
   teleport artifacts are explicit: wait threshold 900 s, junction blockers
   ignored after 60 s. Teleports are reported as a KPI, never hidden.
6. **Metrics:** summary + tripinfo + `edgeData` intervals (300 s). SUMO's
   `queue-output` produced ~230 MB per run and was abandoned; port congestion is
   reported as approach waiting time and minimum approach speed, plus measured
   port throughput (arrivals at the destination edge).

## Baseline results (2026-09-15, 06:00-10:00, seed 42)

| KPI | Value |
|---|---|
| Demand planned / routed / inserted | 10,676 / 10,357 / 9,019 |
| Arrived / running at end | 7,117 / 1,902 |
| Teleports (900 s wait) | 448 (~5% of inserted) |
| Mean trip duration / time loss | 1,148 s / 1,027 s |
| Port throughput (mean / peak) | 1,779 / 2,244 veh/h (~82% of 2,720 target at peak) |
| Port approach waiting time (total) | 3,617 s |
| Metering program | 53.2 s cycle, 40.2 s port green, 2 lanes |

## Consequences

- Absolute numbers are not predictions; only scenario deltas at identical
  demand, seed, and network are comparable (the D5 report format enforces this).
- The measured port throughput (1,779 veh/h mean) sits below the calibrated
  capacity because of saturation losses and upstream spillback — the metering
  program defines an upper bound, not a guarantee.
- Teleports (~5%) and the demand factor (0.75) are documented distortions.
  Improving either means better demand data (hourly counts), not more tuning.
- Residential streets, pedestrians, and southbound traffic are excluded; the US
  side is a stub only.
