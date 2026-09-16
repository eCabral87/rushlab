---
name: run-scenario-study
description: Use when running a traffic scenario study for an area: baseline simulation, intervention scenarios, signal optimization, and the ranked before/after report. Trigger keywords: scenario, baseline, simulate, optimize signals, compare, report.
---

# Run a Scenario Study

## Goal

Produce a reproducible, assumption-documented comparison of traffic interventions
for a registered area.

## Procedure

1. **Define the study.**
   - Area (must exist in `src/rushlab/config/areas.yaml`)
   - Time window (default: `06:00-10:00` for the morning peak)
   - Scenarios: baseline plus one or more interventions (signal retiming, lane-split
     change, ramp metering, demand reroute share, departure staggering)

2. **Run the baseline.**
   ```bash
   uv run rushlab simulate <area> --window 06:00-10:00 --seed 42
   ```
   Confirm the baseline is sane before optimizing anything: total vehicles entered
   vs left, queue spillback present at the border sink, no teleport avalanche
   (teleports > 1% of trips invalidates the run).

3. **Optimize signals** (if in scope):
   ```bash
   uv run rushlab optimize-signals <area> --window 06:00-10:00 --algorithm ga
   ```
   Export the winning plan; never hand-edit timing plans into reports.

4. **Run scenarios, same seed and demand.**
   Only the intervention may change between baseline and scenario.

5. **Generate the report.**
   ```bash
   uv run rushlab report <area> --scenarios baseline,<scenario>...
   ```
   The report must include: ranked before/after table (delay, queue length, CO2),
   the exact command lines, and an assumptions section.

## Rules

- One variable at a time; do not bundle interventions in a single scenario.
- Same seed, same demand for all runs in a study.
- Numbers in docs/README must come from a committed, re-runnable command.
- Never phrase results as predictions of the real world; phrase as
  "under assumptions A, B, C, scenario X ranks above Y".
- If calibration to BTS/CBP data is stale or missing, say so at the top of the report.

## MCP alternative

When the RushLab MCP server is available, prefer its typed tools over shelling
out: `area_analysis`, `area_calibration`, `run_simulation`, `compare_scenarios`,
`render_report`. `optimize_signals` requires `confirm=true` because it runs for
tens of minutes; announce long runs to the user before starting them.
