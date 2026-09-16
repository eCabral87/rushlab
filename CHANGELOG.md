# Changelog

Format follows the project's own release procedure
(`agent/skills/release-notes/SKILL.md`); versions are semver. Release checklist
for v0.1.0: tag `v0.1.0` and create the GitHub release once the tree is reviewed.

## v0.1.0 — 2026-09-16 (tag pending)

First public version: an agent-driven traffic scenario lab for the San Ysidro
border approach, plus the agentic-development evidence layer.

### Added

- **Network layer** — OSM ingestion, analytic travel-time graph with calibrated
  speed fallbacks, synthetic border sink, connectivity/bottleneck/min-cut
  analytics and CLI (`analyze`) (`24b0752`)
- **Demand layer** — BTS Socrata volumes (port 2504), CBP wait-time snapshots
  (committed series), demand-anchored sink calibration with explicit ranges and
  provenance (`168def3`)
- **SUMO microsimulation** — main-road network via `netconvert`, forced and
  metered port entry signal, gateway-based demand, deterministic routing, KPI
  extraction (`58c51ab`)
- **Signal optimization** — Webster cycle/splits with a common corridor cycle,
  DEAP genetic algorithm over offsets (light/full budgets), `simulate --signals`
  and the committed comparison report pipeline (`2c15d76`)
- **MCP server** — 8 domain tools over stdio (`rushlab-mcp`), registered for
  opencode, Claude Code, and Codex from one neutral source (`8ead6ee`)
- **Agentic benchmarks** — deterministic Graphify token benchmark, plan-vs-
  execute A/B, skill-efficacy study; recorded results in `evals/RESULTS.md`
  (`06996ae`)
- **Agent-agnostic tooling** — skills/MCP/hooks defined once under `agent/`,
  generated per-tool configs, CI drift enforcement and `agent_doctor` (`bc82d1e`)
- **Release process** — the `release-notes` skill plus CI (lint, format, types,
  doctor, tests) and MIT license

### Changed

- Simulation bbox refined to the Mexico-side approach with a short US-side stub
  (`32.530, -117.050, 32.545, -117.008`)
- Agent skills mirrored for Claude Code and Codex (`347d33f`), later replaced by
  generated mirrors from neutral sources
- Dependencies trimmed: `traci` and `pulp` removed; `sumolib` declared explicitly

### Fixed

- HTML report rendered empty value cells due to a Jinja `dict.values` name
  collision; regression test added (`90a4a13`)

### Evidence at this release

- 98 tests, 8 ADRs (`docs/decisions/0001`–`0008`), CI green
- Signal study report: `docs/reports/san-ysidro-signal-optimization.html`
- Benchmarks: Graphify focused retrieval −90.7% tokens vs grep+read (20/20
  symbols resolved); plan-first ≈2× tokens on small tasks; skill 4/4 vs 3/4
  rubric at ~1.9× tokens
- Headline traffic finding: the metered border port, not signal timing, is the
  binding constraint (throughput +3.5%, delay −0.7% from retiming eight signals)
