# 0001 — Project scope and modeling assumptions

- Status: accepted
- Date: 2026-09-15

## Context

RushLab must answer intervention questions ("how to cut morning delay at the San
Ysidro approach", "what is the best signal setup") credibly while being honest
about data availability. Real traffic counts, origin–destination matrices, and
signal phasing for Tijuana are not publicly available at intersection level.

## Decisions

1. **Study area: San Ysidro border approach, Tijuana.**
   bbox `32.525,-117.06,32.555,-116.97`. Recon 2026-09-15: ~7,500 highway ways,
   200 traffic-signal nodes (`data/raw/recon_san-ysidro.json`).

2. **Northbound focus for v0.1.** The dominant congestion problem is northbound
   queues into the port. Southbound and US-side networks are out of scope.

3. **Border crossing is a capacity-controlled sink.** Lane types (General, Ready,
   SENTRI) are modeled as separate sink edges with throughput calibrated from
   CBP wait-time data. The queue that spills back into city streets is the
   object of study.

4. **Demand calibration anchors:** BTS monthly inbound personal-vehicle volumes
   (port level) for magnitude; CBP historical wait times for service rates.

5. **Results are relative rankings under documented assumptions, never
   predictions.** Reports must open with assumptions and data vintages.

6. **Simulation engine: SUMO** (pip wheel), controlled via TraCI. Signal timing
   optimization: Webster baseline + genetic algorithm; RL deferred.

## Consequences

- Absolute travel-time numbers are scenario-relative; only deltas between
  scenarios run with identical seed/demand are comparable.
- Missing phasing and turn restrictions must be listed as assumptions in every
  area's documentation.
- Calibration quality becomes a first-class deliverable, not a footnote.
