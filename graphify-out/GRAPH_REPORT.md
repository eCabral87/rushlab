# Graph Report - rushlab  (2026-09-16)

## Corpus Check
- 110 files · ~33,231 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 2, .toml 1, .jsonl 1)

## Summary
- 795 nodes · 1514 edges · 69 communities (48 shown, 21 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8ead6eee`
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
- agent_runner.py
- network/__init__.py
- mcp_server.py
- bts.py
- demand/__init__.py
- demand.py
- runner.py
- sim/__init__.py
- study.py
- evaluator.py
- build_comparison
- test_demand.py
- RushLab benchmark results
- report/__init__.py
- test_mcp_server.py
- merge_ranges
- html.py
- slugify
- calibration.py
- fetch_area
- README.md
- 0003 — Network model and analytic assumptions
- 0004 — Demand model and sink calibration
- 0005 — SUMO microsimulation model
- 0006 — Signal optimization methodology and results
- 0008 — Benchmark methodology
- 0007 — MCP server for agent-driven workflows
- summarize.py
- Changelog
- mini/__init__.py
- evals/__init__.py
- merge_intervals/AGENTS.md
- merge_intervals/README.md
- release_notes/README.md
- slugify/AGENTS.md
- slugify/README.md
- mini

## God Nodes (most connected - your core abstractions)
1. `Area` - 39 edges
2. `optimize_area_signals()` - 22 edges
3. `prepare_baseline()` - 20 edges
4. `analyze_area()` - 19 edges
5. `run_scenario()` - 19 edges
6. `build_analysis_graph()` - 17 edges
7. `get_area()` - 16 edges
8. `gateway_edges()` - 15 edges
9. `find_metering_target()` - 14 edges
10. `read_net()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `analyze_area()` --calls--> `median()`  [INFERRED]
  src/rushlab/network/metrics.py → evals/graphify_tokens.py
- `test_bts_requires_expected_columns()` --calls--> `volumes_from_rows()`  [EXTRACTED]
  tests/test_demand.py → src/rushlab/demand/bts.py
- `test_travel_time_to_sink()` --calls--> `travel_time_to_sink()`  [EXTRACTED]
  tests/test_network_build.py → src/rushlab/network/metrics.py
- `test_parse_opencode_events_sums_steps()` --calls--> `parse_opencode_events()`  [EXTRACTED]
  tests/test_evals.py → evals/agent_runner.py
- `test_parse_codex_events_takes_cumulative_max()` --calls--> `parse_codex_events()`  [EXTRACTED]
  tests/test_evals.py → evals/agent_runner.py

## Import Cycles
- None detected.

## Communities (69 total, 21 thin omitted)

### Community 0 - "opencode.json"
Cohesion: 0.15
Nodes (12): command, enabled, type, instructions, mcp, graphify, rushlab, plugin (+4 more)

### Community 1 - "RushLab — Agent Guide"
Cohesion: 0.25
Nodes (7): Architecture map, Commands, Data sources, Domain rules, Knowledge graph, RushLab — Agent Guide, Working rules

### Community 2 - "RushLab"
Cohesion: 0.14
Nodes (14): Benchmarks (agentic evidence, 2026-09), Data, Demand baseline (2026-09-15), MCP server, Network baseline (2026-09-15), Quickstart, Recon baseline (2026-09), RushLab (+6 more)

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
Cohesion: 0.11
Nodes (24): MultiDiGraph, attach_border_sink(), build_analysis_graph(), _edge_attributes(), edge_capacity_veh_h(), edge_name(), load_osm_graph(), nearest_node() (+16 more)

### Community 28 - "Area"
Cohesion: 0.06
Nodes (55): BBox, Coordinate, Build the SUMO network for an area and print stats., sim_network_command(), Area, BorderConfig, get_area(), load_areas() (+47 more)

### Community 29 - "cli.py"
Cohesion: 0.12
Nodes (28): callback, command, analyze(), _area_or_exit(), areas(), build_area_command(), _calibration_path(), demand() (+20 more)

### Community 30 - "agent_runner.py"
Cohesion: 0.07
Nodes (54): diff_stats(), _find_token_usage(), fresh_workdir(), parse_claude_result(), parse_codex_events(), parse_opencode_events(), Any, Path (+46 more)

### Community 32 - "mcp_server.py"
Cohesion: 0.13
Nodes (27): area_analysis(), area_calibration(), _area_or_error(), compare_scenarios(), list_areas(), main(), optimize_signals(), _parse_window() (+19 more)

### Community 33 - "bts.py"
Cohesion: 0.29
Nodes (10): fetch_volumes(), latest_month(), load_volumes(), Any, DataFrame, Path, BTS Border Crossing/Entry Data client (Socrata)., Return the cached raw BTS payload path, downloading when needed. (+2 more)

### Community 35 - "demand.py"
Cohesion: 0.13
Nodes (28): haversine_m(), _allocate(), boundary_nodes(), destination_edge(), gateway_edges(), node_lonlat(), plan_trips(), Any (+20 more)

### Community 36 - "runner.py"
Cohesion: 0.10
Nodes (39): Per-signal approach flows and critical flow ratios from edgeData., apply_program_to_net(), apply_programs_to_net(), find_metering_target(), metering_program(), MeteringTarget, parse_net_structure(), program_summary() (+31 more)

### Community 38 - "study.py"
Cohesion: 0.08
Nodes (44): build_tls_flow_table(), load_edge_flows(), Any, Path, Total vehicles per edge over the analysis window (from edgeData)., Critical flow ratio per green phase for every traffic light. Ratios are flow /…, build_tls_flow_ranking(), default_signal_path() (+36 more)

### Community 39 - "evaluator.py"
Cohesion: 0.13
Nodes (22): evaluate_candidate(), _evaluate_job(), evaluate_many(), EvaluatorConfig, _parse_candidate_outputs(), Any, Path, Candidate evaluation for signal optimization. Each candidate patches the base… (+14 more)

### Community 40 - "build_comparison"
Cohesion: 0.26
Nodes (11): build_comparison(), Any, Scenario comparison tables., Ranked KPI table with percent deltas against the first scenario (baseline)., render_report(), fake_summary(), Path, Report comparison and rendering tests. (+3 more)

### Community 41 - "test_demand.py"
Cohesion: 0.08
Nodes (36): append_snapshot(), _clean_lane(), fetch_snapshot(), normalize_port(), Any, Path, CBP Border Wait Times live client and snapshot series., Return a normalized CBP wait-time snapshot for the area's port. (+28 more)

### Community 42 - "RushLab benchmark results"
Cohesion: 0.18
Nodes (9): Honesty rules (also in ADR-0008), How to run, RushLab benchmarks, Graphify token reduction, Observations, Plan vs execute (A/B), RushLab benchmark results, Skill efficacy (release-notes) (+1 more)

### Community 44 - "test_mcp_server.py"
Cohesion: 0.08
Nodes (27): RushLab — agent-driven traffic scenario lab for border corridors., Path, CLI smoke tests; no network access., test_analyze_writes_report(), test_build_area_with_cached_fixture(), test_demand_writes_calibration(), mcp_paths(), fixture (+19 more)

### Community 45 - "merge_ranges"
Cohesion: 0.27
Nodes (9): merge_ranges(), Interval merging utilities., Merge overlapping [start, end] intervals. Known issues (see tests): input is…, Interval merge tests (currently failing)., test_handles_contained(), test_handles_unsorted_input(), test_keeps_disjoint(), test_merges_overlapping() (+1 more)

### Community 46 - "html.py"
Cohesion: 0.43
Nodes (7): build_kpi_figure(), build_port_throughput_figure(), build_trip_duration_figure(), _figure_to_base64(), Any, Path, Self-contained HTML comparison report with embedded figures.

### Community 47 - "slugify"
Cohesion: 0.31
Nodes (8): Convert text to a URL-friendly slug. Current behavior: lowercase, non-…, slugify(), Slugify tests (currently failing)., test_existing_behavior(), test_folds_unicode_accents(), test_max_length_never_trails_hyphen(), test_max_length_none_keeps_everything(), test_max_length_truncates_on_word_boundary()

### Community 48 - "calibration.py"
Cohesion: 0.31
Nodes (9): calibrate(), capacity_range(), load_calibration(), Any, Path, Demand-anchored border sink calibration with explicit ranges., Graph build overrides derived from a calibration result., sink_overrides() (+1 more)

### Community 49 - "fetch_area"
Cohesion: 0.47
Nodes (5): area_cache_dir(), fetch_area(), Path, Download and cache the OSM drive network for a study area., Return the cached GraphML path, downloading via Overpass when needed. osmnx…

### Community 50 - "README.md"
Cohesion: 0.29
Nodes (4): 0001 — Project scope and modeling assumptions, Consequences, Context, Decisions

### Community 51 - "0003 — Network model and analytic assumptions"
Cohesion: 0.33
Nodes (5): 0003 — Network model and analytic assumptions, Baseline results (2026-09-15, OSM extract), Consequences, Context, Decisions

### Community 52 - "0004 — Demand model and sink calibration"
Cohesion: 0.33
Nodes (5): 0004 — Demand model and sink calibration, Calibrated baseline (2026-09-15), Consequences, Context, Decisions

### Community 53 - "0005 — SUMO microsimulation model"
Cohesion: 0.33
Nodes (5): 0005 — SUMO microsimulation model, Baseline results (2026-09-15, 06:00-10:00, seed 42), Consequences, Context, Decisions

### Community 54 - "0006 — Signal optimization methodology and results"
Cohesion: 0.33
Nodes (6): 0006 — Signal optimization methodology and results, Consequences and next levers, Context, Decisions, Findings, Results (2026-09-15, seed 42, demand factor 0.75)

### Community 55 - "0008 — Benchmark methodology"
Cohesion: 0.33
Nodes (5): 0008 — Benchmark methodology, Context, Decisions, Honest limits, Recorded results (2026-09-16, opencode, configured default model)

### Community 56 - "0007 — MCP server for agent-driven workflows"
Cohesion: 0.40
Nodes (4): 0007 — MCP server for agent-driven workflows, Consequences, Context, Decisions

## Knowledge Gaps
- **117 isolated node(s):** `graphify-mcp`, `rushlab-mcp`, `mini`, `$schema`, `instructions` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 326 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `analyze_area()` connect `metrics.py` to `mcp_server.py`, `Area`, `cli.py`, `agent_runner.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `median()` connect `agent_runner.py` to `metrics.py`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **What connects `graphify-mcp`, `rushlab-mcp`, `mini` to the rest of the system?**
  _117 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `RushLab` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `build.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._
- **Should `Area` be split into smaller, more focused modules?**
  _Cohesion score 0.05734767025089606 - nodes in this community are weakly interconnected._
- **Should `cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12413793103448276 - nodes in this community are weakly interconnected._