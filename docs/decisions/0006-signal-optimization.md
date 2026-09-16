# 0006 — Signal optimization methodology and results

- Status: accepted
- Date: 2026-09-15

## Context

The D4 baseline leaves the corridor oversaturated with a metered port entry that
encodes the calibrated border capacity (2,720 veh/h). 48 signals exist; the
median signal carries 141 vehicles over the 4-hour window while the busiest
non-port signals carry 1,000-2,200. Optimizing empty intersections adds noise,
not value.

## Decisions

1. **Scope:** the top **8** signals by measured baseline approach flow
   (edgeData), with the metered port junction **excluded by design** — its
   timing encodes the border capacity and must not be retimed.
2. **Webster retiming** (`signals/webster.py`): `C0 = (1.5L + 5) / (1 - Y)`
   from measured critical flow ratios, clamped to 30-120 s; lost time =
   yellow/clearance durations + 2 s startup per phase; minimum green 8 s;
   splits proportional to critical ratios. A **common corridor cycle** (the
   longest plan) is used so offsets are meaningful.
3. **GA offsets** (`signals/optimizer.py`, DEAP): per-junction offsets in
   `[0, cycle)`, tournament selection, blend crossover, wrapped Gaussian
   mutation. Budget presets: `light` (16 x 12, the default) and `full` (24 x 20).
4. **Evaluation** (`signals/evaluator.py`): each candidate patches the metered
   net with its programs/offsets and runs SUMO in a private directory over
   06:00-08:00, four evaluations in parallel. SUMO 1.27 cannot change TLS
   offsets via TraCI, so patched nets are the exact route (documented deviation
   from the libsumo idea; no new dependency).
5. **Fitness:** `total_time_loss_s + 600 x teleports - 20 x arrived` — delay
   dominates, teleports are penalized, arrivals are rewarded.
6. **Validation:** the winning program is applied to the full 06:00-10:00
   window with identical demand and seed, and compared through the report
   pipeline (`rushlab report`); the report is committed as evidence.

## Results (2026-09-15, seed 42, demand factor 0.75)

| KPI | Baseline | Optimized | Δ |
|---|---|---|---|
| Mean time loss (s) | 1,026.7 | 1,019.6 | -0.7% |
| Mean trip duration (s) | 1,148.1 | 1,140.6 | -0.7% |
| Port throughput (veh/h) | 1,779.2 | 1,841.0 | +3.5% |
| Port throughput peak (veh/h) | 2,244.0 | 2,244.0 | 0% |
| Port approach waiting (s) | 3,617.0 | 3,661.0 | +1.2% |
| Teleports | 448 | 486 | +8.5% |
| Arrived vehicles | 7,117 | 7,364 | +3.5% |

GA progress: evaluation-window fitness improved from 2,105,645 to 2,097,037
(-0.4%) over 166 evaluations; common cycle 48.1 s; offsets 13-40 s.

## Findings

- **The metered port, not upstream signals, is the binding constraint.**
  Retiming eight signals moves throughput by ~3.5% and delay by <1%, while
  teleports slightly worsen. This is the expected outcome at a bottleneck whose
  capacity is fixed by policy, and it is the honest headline of the study.
- Webster cycles for most selected signals are short (Y between 0.04 and 0.31),
  so several phases sit at the 8 s minimum green — the corridor is not
  demand-saturated at the intersection level; the queue is port spillback.
- Peak port throughput is identical in both scenarios (2,244 veh/h), confirming
  the metering program caps the boundary exactly as designed.

## Consequences and next levers

- Results are single-seed and window-sensitive; only deltas under identical
  demand/seed/network are comparable.
- The GA optimizes a 2 h window but validates on 4 h; transfer is imperfect by
  construction (documented, not hidden).
- Next meaningful levers are demand-side and policy-side, not green splits:
  metering policy (green split at the port), lane management (Ready/SENTRI
  shares), departure staggering, and reroute shares to Otay Mesa.
- The report pipeline (`rushlab report`) is scenario-agnostic and will be reused
  for those studies.
