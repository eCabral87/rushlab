# 0004 — Demand model and sink calibration

- Status: accepted
- Date: 2026-09-15

## Context

D2 attached a placeholder border sink (4,800 veh/h, fixed 30 s connector) and
flagged it for calibration. Public data available:

- **BTS Border Crossing/Entry Data** (Socrata API): monthly inbound volumes per
  port — San Ysidro `port_code=2504`, measures include Personal Vehicles and
  Pedestrians. Latest vintage at calibration: 2026-07 (~6-week lag).
- **CBP Border Wait Times** (`bwt.cbp.gov/api/bwtnew`): live per-lane-type
  readings (General / Ready / SENTRI / pedestrian) with open lanes and delays.
- **No programmatic historical wait-time API.** The data.gov dataset only links
  the live site; the historical page exposes no documented interface.

## Decisions

1. **Demand anchor:** BTS trailing 12-month mean of daily Personal Vehicles
   (monthly totals divided by days in month). At calibration: **43,057 veh/day**.
2. **Hourly shape:** a documented commuter profile (normalized weights, peak
   06:00–10:00) informed by CBP morning wait-time peaks. Peak-hour demand:
   **4,152 veh/h**. This is an assumption, explicitly not measured hourly demand.
3. **Capacity range:** design POV lanes (34) x 3600 / primary-inspection time,
   with service times {low: 60 s, central: 45 s, high: 30 s}:
   **2,040 / 2,720 / 4,080 veh/h**. Central is used for the analytic graph
   override. Peak utilisation 1.53 at central capacity — consistent with the
   observed queues and the documented delays.
4. **Wait evidence:** each `rushlab demand` run appends the CBP snapshot to
   `data/derived/<area>/wait_snapshots.jsonl` (committed, deduplicated). The
   calibration records the snapshot it used; a real series accumulates over time.
5. **Graph integration:** calibrated central capacity replaces the area
   placeholder; the observed General-lane wait becomes the sink connector delay,
   so travel-time-to-border includes queueing. `--no-calibrated` restores
   placeholders.
6. **Evidence committed:** `data/derived/<area>/calibration.json` with full
   provenance (source vintage, profile, service-time assumptions, snapshot).
   Raw API responses stay in the ignored cache.

## Calibrated baseline (2026-09-15)

| Item | Value |
|---|---|
| BTS trailing daily average (Personal Vehicles) | 43,057 (vintage 2026-07) |
| Peak-hour demand | 4,152 veh/h |
| Sink capacity (low / central / high) | 2,040 / 2,720 / 4,080 veh/h |
| Peak utilisation (central) | 1.53 |
| Observed snapshot (2026-09-15) | General 170 min wait, 4 lanes open |
| Median travel time to sink (calibrated run) | 10,478 s (~2.9 h, queue-inclusive) |
| Min cut to sink (via-rapida-west) | 2,720 veh/h (central capacity) |

## Consequences

- Median travel time to the sink is **queue-inclusive and snapshot-specific** —
  it reflects the observation used, not a daily average. Subsequent runs will
  use the accumulated series (median) to reduce single-sample bias.
- The profile remains an assumption until snapshots or external counts support a
  measured hourly shape.
- Pedestrians are published by BTS but not modeled in v0.1 (vehicle focus).
- No outbound data exists; all demand refers to northbound crossings.
- Absolute numbers are estimates with stated ranges; only scenario deltas under
  identical assumptions are comparable.
