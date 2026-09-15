# Graph Report - rushlab  (2026-09-15)

## Corpus Check
- 47 files · ~219,738 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 2, .toml 1, .graphml 1)

## Summary
- 289 nodes · 434 edges · 32 communities (26 shown, 6 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bc82d1ee`
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

## God Nodes (most connected - your core abstractions)
1. `Area` - 16 edges
2. `analyze_area()` - 16 edges
3. `build_analysis_graph()` - 15 edges
4. `build_outputs()` - 12 edges
5. `get_area()` - 11 edges
6. `fetch_area()` - 10 edges
7. `load_areas()` - 9 edges
8. `RushLab` - 9 edges
9. `analyze()` - 8 edges
10. `top_signal_bottlenecks()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `mini_area()` --calls--> `BorderConfig`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/config/__init__.py
- `test_missing_crossing_node_raises()` --calls--> `BorderConfig`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/config/__init__.py
- `mini_area()` --references--> `Area`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/config/__init__.py
- `test_load_areas_includes_san_ysidro()` --calls--> `load_areas()`  [EXTRACTED]
  tests/test_areas.py → src/rushlab/config/__init__.py
- `test_border_metadata_parsed()` --calls--> `get_area()`  [EXTRACTED]
  tests/test_areas.py → src/rushlab/config/__init__.py

## Import Cycles
- None detected.

## Communities (32 total, 6 thin omitted)

### Community 0 - "opencode.json"
Cohesion: 0.25
Nodes (7): enabled, type, instructions, mcp, graphify, plugin, $schema

### Community 1 - "RushLab — Agent Guide"
Cohesion: 0.25
Nodes (7): Architecture map, Commands, Data sources, Domain rules, Knowledge graph, RushLab — Agent Guide, Working rules

### Community 2 - "RushLab"
Cohesion: 0.10
Nodes (18): 0001 — Project scope and modeling assumptions, Consequences, Context, Decisions, 0003 — Network model and analytic assumptions, Baseline results (2026-09-15, OSM extract), Consequences, Context (+10 more)

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
Cohesion: 0.17
Nodes (31): analyze_area(), connectivity_summary(), edge_betweenness(), min_cut_to_sink(), node_betweenness(), _node_entry(), node_name(), Any (+23 more)

### Community 27 - "build.py"
Cohesion: 0.11
Nodes (25): fixture, MultiDiGraph, attach_border_sink(), build_analysis_graph(), _edge_attributes(), edge_capacity_veh_h(), edge_name(), haversine_m() (+17 more)

### Community 28 - "config/__init__.py"
Cohesion: 0.11
Nodes (26): BBox, Coordinate, integration, BorderConfig, get_area(), load_areas(), _parse_area(), _parse_border() (+18 more)

### Community 29 - "cli.py"
Cohesion: 0.13
Nodes (22): callback, command, analyze(), _area_or_exit(), areas(), build_area_command(), fetch_area_command(), main() (+14 more)

### Community 30 - "test_cli.py"
Cohesion: 0.20
Nodes (4): RushLab — agent-driven traffic scenario lab for border corridors., Path, CLI smoke tests; no network access., test_analyze_writes_report()

## Knowledge Gaps
- **71 isolated node(s):** `uv`, `graphify-mcp`, `$schema`, `instructions`, `plugin` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 148 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Area` connect `cli.py` to `metrics.py`, `build.py`, `config/__init__.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `command` connect `cli.py` to `opencode.json`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `build_analysis_graph()` connect `build.py` to `cli.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `uv`, `graphify-mcp`, `$schema` to the rest of the system?**
  _71 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `RushLab` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10887096774193548 - nodes in this community are weakly interconnected._
- **Should `config/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10837438423645321 - nodes in this community are weakly interconnected._