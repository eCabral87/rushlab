# Graph Report - rushlab  (2026-09-15)

## Corpus Check
- 83 files · ~25,005 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 2, .toml 1, .jsonl 1)

## Summary
- 601 nodes · 1168 edges · 44 communities (35 shown, 9 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `58c51abc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- opencode.json
- RushLab — Agent Guide
- RushLab
- sync_agent_config.py
- test_agent_configs.py
- project_root
- Add a Study Area
- recon_overpass.py
- Release Notes and Versioning
- Raw data
- Run a Scenario Study
- rushlab
- Add a Study Area
- Release Notes and Versioning
- Run a Scenario Study
- Add a Study Area
- Release Notes and Versioning
- Run a Scenario Study
- 0002 — Agent-agnostic tooling layout
- Add a Study Area
- Release Notes and Versioning
- Run a Scenario Study
- graphify
- graphify.js
- agent/README.md
- CLAUDE.md
- metrics.py
- build.py
- Area
- cli.py
- test_cli.py
- network/__init__.py
- test_demand.py
- demand
- demand/__init__.py
- demand.py
- runner.py
- sim/__init__.py
- study.py
- evaluator.py
- report
- calibration.py
- cbp.py
- report/__init__.py

## God Nodes (most connected - your core abstractions)
1. `Area` - 37 edges
2. `optimize_area_signals()` - 20 edges
3. `prepare_baseline()` - 20 edges
4. `run_scenario()` - 17 edges
5. `analyze_area()` - 16 edges
6. `build_analysis_graph()` - 15 edges
7. `gateway_edges()` - 15 edges
8. `get_area()` - 14 edges
9. `find_metering_target()` - 14 edges
10. `read_net()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `test_peak_share_in_plausible_range()` --calls--> `peak_share()`  [EXTRACTED]
  tests/test_demand.py → src/rushlab/demand/profile.py
- `test_travel_time_to_sink()` --calls--> `travel_time_to_sink()`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/network/metrics.py
- `demand()` --references--> `command`  [EXTRACTED]
  src/rushlab/cli.py → opencode.json
- `report()` --references--> `command`  [EXTRACTED]
  src/rushlab/cli.py → opencode.json
- `mini_area()` --calls--> `BorderConfig`  [EXTRACTED]
  tests/conftest.py → src/rushlab/config/__init__.py

## Import Cycles
- None detected.

## Communities (44 total, 9 thin omitted)

### Community 0 - "opencode.json"
Cohesion: 0.25
Nodes (7): enabled, type, instructions, mcp, graphify, plugin, $schema

### Community 1 - "RushLab — Agent Guide"
Cohesion: 0.25
Nodes (7): Architecture map, Commands, Data sources, Domain rules, Knowledge graph, RushLab — Agent Guide, Working rules

### Community 2 - "RushLab"
Cohesion: 0.05
Nodes (37): 0001 — Project scope and modeling assumptions, Consequences, Context, Decisions, 0003 — Network model and analytic assumptions, Baseline results (2026-09-15, OSM extract), Consequences, Context (+29 more)

### Community 3 - "sync_agent_config.py"
Cohesion: 0.21
Nodes (18): check(), main(), Verify the agent setup: generated files, config parsing, and graph presence.…, build_outputs(), claude_mcp_config(), claude_settings(), codex_config(), codex_hooks() (+10 more)

### Community 4 - "test_agent_configs.py"
Cohesion: 0.33
Nodes (6): load_json(), Generated agent configuration must stay valid and in sync., test_agent_sources_parse(), test_claude_mcp_config(), test_opencode_config_has_instructions_and_mcp(), test_session_start_hooks_exist()

### Community 5 - "project_root"
Cohesion: 0.40
Nodes (5): main(), project_root(), Path, Print a knowledge-graph hint when graphify-out/graph.json exists. Used by agent…, Resolve the git top-level, falling back to the repo layout.

### Community 6 - "Add a Study Area"
Cohesion: 0.40
Nodes (4): Add a Study Area, Goal, Procedure, Rules

### Community 7 - "recon_overpass.py"
Cohesion: 0.50
Nodes (4): main(), overpass_count(), Reproduce OSM reconnaissance counts for a study-area bounding box. Usage: uv…, Return the total count of elements matching selector inside bbox.

### Community 8 - "Release Notes and Versioning"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Release Notes and Versioning, Rules

### Community 10 - "Run a Scenario Study"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Rules, Run a Scenario Study

### Community 12 - "Add a Study Area"
Cohesion: 0.40
Nodes (4): Add a Study Area, Goal, Procedure, Rules

### Community 13 - "Release Notes and Versioning"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Release Notes and Versioning, Rules

### Community 14 - "Run a Scenario Study"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Rules, Run a Scenario Study

### Community 15 - "Add a Study Area"
Cohesion: 0.40
Nodes (4): Add a Study Area, Goal, Procedure, Rules

### Community 16 - "Release Notes and Versioning"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Release Notes and Versioning, Rules

### Community 17 - "Run a Scenario Study"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Rules, Run a Scenario Study

### Community 18 - "0002 — Agent-agnostic tooling layout"
Cohesion: 0.40
Nodes (4): 0002 — Agent-agnostic tooling layout, Consequences, Context, Decisions

### Community 19 - "Add a Study Area"
Cohesion: 0.40
Nodes (4): Add a Study Area, Goal, Procedure, Rules

### Community 20 - "Release Notes and Versioning"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Release Notes and Versioning, Rules

### Community 21 - "Run a Scenario Study"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Rules, Run a Scenario Study

### Community 22 - "graphify"
Cohesion: 0.50
Nodes (3): uv, graphify, graphify-mcp

### Community 26 - "metrics.py"
Cohesion: 0.18
Nodes (30): analyze_area(), connectivity_summary(), edge_betweenness(), min_cut_to_sink(), node_betweenness(), _node_entry(), node_name(), Any (+22 more)

### Community 27 - "build.py"
Cohesion: 0.10
Nodes (27): MultiDiGraph, BorderConfig, Border-crossing metadata used to attach the synthetic sink., attach_border_sink(), build_analysis_graph(), _edge_attributes(), edge_capacity_veh_h(), edge_name() (+19 more)

### Community 28 - "Area"
Cohesion: 0.06
Nodes (53): BBox, Coordinate, Area, get_area(), load_areas(), _parse_area(), _parse_border(), _parse_coordinate() (+45 more)

### Community 29 - "cli.py"
Cohesion: 0.12
Nodes (26): callback, command, analyze(), _area_or_exit(), areas(), build_area_command(), _calibration_path(), fetch_area_command() (+18 more)

### Community 30 - "test_cli.py"
Cohesion: 0.18
Nodes (6): RushLab — agent-driven traffic scenario lab for border corridors., Path, CLI smoke tests; no network access., test_analyze_writes_report(), test_build_area_with_cached_fixture(), test_demand_writes_calibration()

### Community 32 - "test_demand.py"
Cohesion: 0.29
Nodes (10): area(), bts_frame(), fixture, Path, Demand-layer tests using committed fixtures; no network access., snapshot(), test_calibration_roundtrip(), test_capacity_range_math() (+2 more)

### Community 33 - "demand"
Cohesion: 0.15
Nodes (19): demand(), Fetch demand data, calibrate the border sink, and write derived evidence., fetch_volumes(), latest_month(), load_volumes(), Any, DataFrame, Path (+11 more)

### Community 35 - "demand.py"
Cohesion: 0.13
Nodes (30): haversine_m(), _allocate(), boundary_nodes(), destination_edge(), gateway_edges(), node_lonlat(), plan_trips(), Any (+22 more)

### Community 36 - "runner.py"
Cohesion: 0.11
Nodes (36): apply_program_to_net(), apply_programs_to_net(), find_metering_target(), metering_program(), MeteringTarget, program_summary(), Path, Fixed-time port metering signal derived from calibrated capacity. (+28 more)

### Community 38 - "study.py"
Cohesion: 0.08
Nodes (47): build_tls_flow_table(), load_edge_flows(), Any, Path, Per-signal approach flows and critical flow ratios from edgeData., Total vehicles per edge over the analysis window (from edgeData)., Critical flow ratio per green phase for every traffic light. Ratios are flow /…, build_tls_flow_ranking() (+39 more)

### Community 39 - "evaluator.py"
Cohesion: 0.13
Nodes (22): evaluate_candidate(), _evaluate_job(), evaluate_many(), EvaluatorConfig, _parse_candidate_outputs(), Any, Path, Candidate evaluation for signal optimization. Each candidate patches the base… (+14 more)

### Community 40 - "report"
Cohesion: 0.16
Nodes (22): Compare scenario summaries and write a self-contained HTML report., report(), build_comparison(), load_scenario_summary(), Any, Path, Scenario comparison tables., Ranked KPI table with percent deltas against the first scenario (baseline). (+14 more)

### Community 41 - "calibration.py"
Cohesion: 0.18
Nodes (18): calibrate(), capacity_range(), load_calibration(), Any, Path, Demand-anchored border sink calibration with explicit ranges., Graph build overrides derived from a calibration result., sink_overrides() (+10 more)

### Community 42 - "cbp.py"
Cohesion: 0.33
Nodes (10): append_snapshot(), _clean_lane(), fetch_snapshot(), normalize_port(), Any, Path, CBP Border Wait Times live client and snapshot series., Return a normalized CBP wait-time snapshot for the area's port. (+2 more)

## Knowledge Gaps
- **87 isolated node(s):** `uv`, `graphify-mcp`, `$schema`, `instructions`, `plugin` (+82 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 250 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Area` connect `Area` to `demand`, `demand.py`, `runner.py`, `study.py`, `cbp.py`, `metrics.py`, `build.py`, `cli.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `optimize_area_signals()` connect `study.py` to `runner.py`, `evaluator.py`, `calibration.py`, `Area`, `cli.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `get_area()` connect `Area` to `test_demand.py`, `demand`, `cli.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **What connects `uv`, `graphify-mcp`, `$schema` to the rest of the system?**
  _87 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `RushLab` be split into smaller, more focused modules?**
  _Cohesion score 0.046511627906976744 - nodes in this community are weakly interconnected._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09982174688057041 - nodes in this community are weakly interconnected._
- **Should `Area` be split into smaller, more focused modules?**
  _Cohesion score 0.058699101004759384 - nodes in this community are weakly interconnected._