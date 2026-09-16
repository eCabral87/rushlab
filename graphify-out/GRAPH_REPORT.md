# Graph Report - rushlab  (2026-09-15)

## Corpus Check
- 68 files · ~19,234 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 2, .toml 1, .jsonl 1)

## Summary
- 481 nodes · 891 edges · 38 communities (30 shown, 8 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `168def3f`
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
- config/__init__.py
- cli.py
- test_cli.py
- network/__init__.py
- test_demand.py
- Area
- demand/__init__.py
- demand.py
- find_metering_target
- sim/__init__.py

## God Nodes (most connected - your core abstractions)
1. `Area` - 35 edges
2. `prepare_baseline()` - 18 edges
3. `analyze_area()` - 16 edges
4. `build_analysis_graph()` - 15 edges
5. `gateway_edges()` - 15 edges
6. `get_area()` - 14 edges
7. `find_metering_target()` - 14 edges
8. `demand()` - 13 edges
9. `read_net()` - 13 edges
10. `build_sumo_network()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_travel_time_to_sink()` --calls--> `travel_time_to_sink()`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/network/metrics.py
- `mini_area()` --calls--> `BorderConfig`  [EXTRACTED]
  tests/conftest.py → src/rushlab/config/__init__.py
- `mini_area()` --references--> `Area`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/config/__init__.py
- `test_route_trips()` --references--> `Area`  [EXTRACTED]
  tests/test_sim_demand.py → src/rushlab/config/__init__.py
- `test_baseline_end_to_end()` --references--> `Area`  [EXTRACTED]
  tests/test_sim_runner.py → src/rushlab/config/__init__.py

## Import Cycles
- None detected.

## Communities (38 total, 8 thin omitted)

### Community 0 - "opencode.json"
Cohesion: 0.25
Nodes (7): enabled, type, instructions, mcp, graphify, plugin, $schema

### Community 1 - "RushLab — Agent Guide"
Cohesion: 0.25
Nodes (7): Architecture map, Commands, Data sources, Domain rules, Knowledge graph, RushLab — Agent Guide, Working rules

### Community 2 - "RushLab"
Cohesion: 0.06
Nodes (30): 0001 — Project scope and modeling assumptions, Consequences, Context, Decisions, 0003 — Network model and analytic assumptions, Baseline results (2026-09-15, OSM extract), Consequences, Context (+22 more)

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

### Community 28 - "config/__init__.py"
Cohesion: 0.08
Nodes (33): BBox, Coordinate, get_area(), load_areas(), _parse_area(), _parse_border(), _parse_coordinate(), Path (+25 more)

### Community 29 - "cli.py"
Cohesion: 0.07
Nodes (55): callback, command, analyze(), _area_or_exit(), areas(), build_area_command(), _calibration_path(), demand() (+47 more)

### Community 30 - "test_cli.py"
Cohesion: 0.18
Nodes (6): RushLab — agent-driven traffic scenario lab for border corridors., Path, CLI smoke tests; no network access., test_analyze_writes_report(), test_build_area_with_cached_fixture(), test_demand_writes_calibration()

### Community 32 - "test_demand.py"
Cohesion: 0.10
Nodes (31): append_snapshot(), _clean_lane(), fetch_snapshot(), normalize_port(), Any, Path, CBP Border Wait Times live client and snapshot series., Return a normalized CBP wait-time snapshot for the area's port. (+23 more)

### Community 33 - "Area"
Cohesion: 0.09
Nodes (32): Area, osmnx expects (left, bottom, right, top) == (west, south, east, north)., fetch_volumes(), load_volumes(), Any, Path, BTS Border Crossing/Entry Data client (Socrata)., Return the cached raw BTS payload path, downloading when needed. (+24 more)

### Community 35 - "demand.py"
Cohesion: 0.13
Nodes (30): haversine_m(), _allocate(), boundary_nodes(), destination_edge(), gateway_edges(), node_lonlat(), plan_trips(), Any (+22 more)

### Community 36 - "find_metering_target"
Cohesion: 0.21
Nodes (18): find_metering_target(), metering_program(), MeteringTarget, _parse_net(), Path, Fixed-time port metering signal derived from calibrated capacity., Retime the port phases so the metered movement matches target throughput. The…, First traffic-light junction upstream of the destination edge. (+10 more)

## Knowledge Gaps
- **81 isolated node(s):** `uv`, `graphify-mcp`, `$schema`, `instructions`, `plugin` (+76 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 206 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Area` connect `Area` to `test_demand.py`, `demand.py`, `metrics.py`, `build.py`, `config/__init__.py`, `cli.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `get_area()` connect `config/__init__.py` to `test_demand.py`, `Area`, `cli.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `command` connect `cli.py` to `opencode.json`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `uv`, `graphify-mcp`, `$schema` to the rest of the system?**
  _81 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `RushLab` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09982174688057041 - nodes in this community are weakly interconnected._
- **Should `config/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08108108108108109 - nodes in this community are weakly interconnected._