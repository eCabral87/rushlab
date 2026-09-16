# Graph Report - rushlab  (2026-09-16)

## Corpus Check
- 86 files · ~27,187 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 2, .toml 1, .jsonl 1)

## Summary
- 671 nodes · 1323 edges · 50 communities (41 shown, 9 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `90a4a132`
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
- network.py
- cli.py
- test_cli.py
- network/__init__.py
- mcp_server.py
- Area
- demand/__init__.py
- demand.py
- runner.py
- sim/__init__.py
- study.py
- evaluator.py
- build_comparison
- test_demand.py
- cbp.py
- report/__init__.py
- test_mcp_server.py
- get_area
- report
- config/__init__.py
- conftest.py
- fetch_area

## God Nodes (most connected - your core abstractions)
1. `Area` - 39 edges
2. `optimize_area_signals()` - 22 edges
3. `prepare_baseline()` - 20 edges
4. `run_scenario()` - 19 edges
5. `analyze_area()` - 18 edges
6. `build_analysis_graph()` - 17 edges
7. `get_area()` - 16 edges
8. `gateway_edges()` - 15 edges
9. `find_metering_target()` - 14 edges
10. `read_net()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `test_travel_time_to_sink()` --calls--> `travel_time_to_sink()`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/network/metrics.py
- `mini_area()` --calls--> `BorderConfig`  [EXTRACTED]
  tests/conftest.py → src/rushlab/config/__init__.py
- `mini_area()` --references--> `Area`  [EXTRACTED]
  tests/conftest.py → src/rushlab/config/__init__.py
- `mini_cache()` --references--> `Area`  [EXTRACTED]
  tests/conftest.py → src/rushlab/config/__init__.py
- `mini_net()` --references--> `Area`  [EXTRACTED]
  tests/conftest.py → src/rushlab/config/__init__.py

## Import Cycles
- None detected.

## Communities (50 total, 9 thin omitted)

### Community 0 - "opencode.json"
Cohesion: 0.15
Nodes (12): command, enabled, type, instructions, mcp, graphify, rushlab, plugin (+4 more)

### Community 1 - "RushLab — Agent Guide"
Cohesion: 0.25
Nodes (7): Architecture map, Commands, Data sources, Domain rules, Knowledge graph, RushLab — Agent Guide, Working rules

### Community 2 - "RushLab"
Cohesion: 0.04
Nodes (42): 0001 — Project scope and modeling assumptions, Consequences, Context, Decisions, 0003 — Network model and analytic assumptions, Baseline results (2026-09-15, OSM extract), Consequences, Context (+34 more)

### Community 3 - "sync_agent_config.py"
Cohesion: 0.21
Nodes (18): check(), main(), Verify the agent setup: generated files, config parsing, and graph presence.…, build_outputs(), claude_mcp_config(), claude_settings(), codex_config(), codex_hooks() (+10 more)

### Community 4 - "test_agent_configs.py"
Cohesion: 0.31
Nodes (7): load_json(), Generated agent configuration must stay valid and in sync., test_agent_sources_parse(), test_claude_mcp_config(), test_opencode_config_has_instructions_and_mcp(), test_rushlab_mcp_registered_in_every_agent_config(), test_session_start_hooks_exist()

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
Cohesion: 0.33
Nodes (5): Goal, MCP alternative, Procedure, Rules, Run a Scenario Study

### Community 12 - "Add a Study Area"
Cohesion: 0.40
Nodes (4): Add a Study Area, Goal, Procedure, Rules

### Community 13 - "Release Notes and Versioning"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Release Notes and Versioning, Rules

### Community 14 - "Run a Scenario Study"
Cohesion: 0.33
Nodes (5): Goal, MCP alternative, Procedure, Rules, Run a Scenario Study

### Community 15 - "Add a Study Area"
Cohesion: 0.40
Nodes (4): Add a Study Area, Goal, Procedure, Rules

### Community 16 - "Release Notes and Versioning"
Cohesion: 0.40
Nodes (4): Goal, Procedure, Release Notes and Versioning, Rules

### Community 17 - "Run a Scenario Study"
Cohesion: 0.33
Nodes (5): Goal, MCP alternative, Procedure, Rules, Run a Scenario Study

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
Cohesion: 0.33
Nodes (5): Goal, MCP alternative, Procedure, Rules, Run a Scenario Study

### Community 22 - "graphify"
Cohesion: 0.40
Nodes (5): uv, graphify, rushlab, graphify-mcp, rushlab-mcp

### Community 26 - "metrics.py"
Cohesion: 0.18
Nodes (30): analyze_area(), connectivity_summary(), edge_betweenness(), min_cut_to_sink(), node_betweenness(), _node_entry(), node_name(), Any (+22 more)

### Community 27 - "build.py"
Cohesion: 0.10
Nodes (27): MultiDiGraph, BorderConfig, Border-crossing metadata used to attach the synthetic sink., attach_border_sink(), build_analysis_graph(), _edge_attributes(), edge_capacity_veh_h(), edge_name() (+19 more)

### Community 28 - "network.py"
Cohesion: 0.17
Nodes (16): build_sumo_network(), fetch_osm_xml(), network_stats(), osm_xml_query(), Any, Path, SUMO network construction from OpenStreetMap XML., Build (or reuse) the SUMO network and return its path plus stats. (+8 more)

### Community 29 - "cli.py"
Cohesion: 0.11
Nodes (31): callback, command, analyze(), _area_or_exit(), areas(), build_area_command(), _calibration_path(), demand() (+23 more)

### Community 30 - "test_cli.py"
Cohesion: 0.18
Nodes (6): RushLab — agent-driven traffic scenario lab for border corridors., Path, CLI smoke tests; no network access., test_analyze_writes_report(), test_build_area_with_cached_fixture(), test_demand_writes_calibration()

### Community 32 - "mcp_server.py"
Cohesion: 0.12
Nodes (27): load_calibration(), Any, Graph build overrides derived from a calibration result., sink_overrides(), area_analysis(), area_calibration(), _area_or_error(), compare_scenarios() (+19 more)

### Community 33 - "Area"
Cohesion: 0.24
Nodes (10): Area, osmnx expects (left, bottom, right, top) == (west, south, east, north)., fetch_volumes(), load_volumes(), Any, Path, BTS Border Crossing/Entry Data client (Socrata)., Return the cached raw BTS payload path, downloading when needed. (+2 more)

### Community 35 - "demand.py"
Cohesion: 0.12
Nodes (32): Build the SUMO network for an area and print stats., sim_network_command(), haversine_m(), _allocate(), boundary_nodes(), destination_edge(), gateway_edges(), node_lonlat() (+24 more)

### Community 36 - "runner.py"
Cohesion: 0.11
Nodes (34): apply_program_to_net(), find_metering_target(), metering_program(), MeteringTarget, program_summary(), Path, Fixed-time port metering signal derived from calibrated capacity., Retime the port phases so the metered movement matches target throughput. The… (+26 more)

### Community 38 - "study.py"
Cohesion: 0.08
Nodes (47): build_tls_flow_table(), load_edge_flows(), Any, Path, Per-signal approach flows and critical flow ratios from edgeData., Total vehicles per edge over the analysis window (from edgeData)., Critical flow ratio per green phase for every traffic light. Ratios are flow /…, build_tls_flow_ranking() (+39 more)

### Community 39 - "evaluator.py"
Cohesion: 0.12
Nodes (24): evaluate_candidate(), _evaluate_job(), evaluate_many(), EvaluatorConfig, _parse_candidate_outputs(), Any, Path, Candidate evaluation for signal optimization. Each candidate patches the base… (+16 more)

### Community 40 - "build_comparison"
Cohesion: 0.23
Nodes (12): build_comparison(), load_scenario_summary(), Any, Path, Scenario comparison tables., Ranked KPI table with percent deltas against the first scenario (baseline)., fake_summary(), Path (+4 more)

### Community 41 - "test_demand.py"
Cohesion: 0.14
Nodes (24): calibrate(), capacity_range(), Demand-anchored border sink calibration with explicit ranges., hourly_demand(), normalized_profile(), peak_hour_demand(), peak_share(), Documented northbound demand profile (assumption, refinable from snapshots). (+16 more)

### Community 42 - "cbp.py"
Cohesion: 0.20
Nodes (14): append_snapshot(), _clean_lane(), fetch_snapshot(), normalize_port(), Any, Path, CBP Border Wait Times live client and snapshot series., Return a normalized CBP wait-time snapshot for the area's port. (+6 more)

### Community 44 - "test_mcp_server.py"
Cohesion: 0.13
Nodes (21): mcp_paths(), fixture, integration, Path, MCP server tool tests, including an in-memory client round trip., test_area_analysis_requires_cached_graph(), test_area_calibration_missing_raises(), test_area_calibration_roundtrip() (+13 more)

### Community 45 - "get_area"
Cohesion: 0.19
Nodes (14): get_area(), load_areas(), Path, Path, Study-area registry tests., test_border_metadata_parsed(), test_invalid_bbox_rejected(), test_load_areas_includes_san_ysidro() (+6 more)

### Community 46 - "report"
Cohesion: 0.32
Nodes (12): Compare scenario summaries and write a self-contained HTML report., report(), Render the comparison HTML report (seconds); output stays under results/ or…, render_report(), build_kpi_figure(), build_port_throughput_figure(), build_trip_duration_figure(), _figure_to_base64() (+4 more)

### Community 47 - "config/__init__.py"
Cohesion: 0.24
Nodes (10): BBox, Coordinate, _parse_area(), _parse_border(), _parse_coordinate(), Study-area registry loaded from areas.yaml., Named gateway used as a source in capacity analysis., Terminal (+2 more)

### Community 48 - "conftest.py"
Cohesion: 0.43
Nodes (6): mini_area(), mini_cache(), mini_net(), fixture, Path, Shared fixtures for SUMO tests; no network access.

### Community 49 - "fetch_area"
Cohesion: 0.47
Nodes (5): area_cache_dir(), fetch_area(), Path, Download and cache the OSM drive network for a study area., Return the cached GraphML path, downloading via Overpass when needed. osmnx…

## Knowledge Gaps
- **99 isolated node(s):** `graphify-mcp`, `rushlab-mcp`, `$schema`, `instructions`, `plugin` (+94 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 278 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Area` connect `Area` to `mcp_server.py`, `demand.py`, `runner.py`, `study.py`, `cbp.py`, `get_area`, `config/__init__.py`, `conftest.py`, `fetch_area`, `metrics.py`, `build.py`, `network.py`, `cli.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `optimize_area_signals()` connect `study.py` to `mcp_server.py`, `Area`, `runner.py`, `evaluator.py`, `cli.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `get_area()` connect `get_area` to `mcp_server.py`, `Area`, `test_demand.py`, `cbp.py`, `config/__init__.py`, `network.py`, `cli.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **What connects `graphify-mcp`, `rushlab-mcp`, `$schema` to the rest of the system?**
  _99 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `RushLab` be split into smaller, more focused modules?**
  _Cohesion score 0.04081632653061224 - nodes in this community are weakly interconnected._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09982174688057041 - nodes in this community are weakly interconnected._
- **Should `cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10984848484848485 - nodes in this community are weakly interconnected._