# 0007 — MCP server for agent-driven workflows

- Status: accepted
- Date: 2026-09-15

## Context

RushLab's pipeline (analysis, calibration, simulation, optimization, reporting)
is exercised through the CLI. Agents work better with typed tool calls than with
guessed shell flags and screen-scraped output. The repo already generates MCP
configuration for opencode, Claude Code, and Codex from `agent/mcp.json`.

## Decisions

1. **Server:** `src/rushlab/mcp_server.py`, stdio transport, console script
   `rushlab-mcp` (configs run `uv run --no-sync rushlab-mcp`). Uses the `mcp`
   2.x API (`mcp.server.mcpserver.MCPServer`; FastMCP was renamed upstream).
2. **Tool surface (8):**
   - read-only: `list_areas`, `area_analysis`, `area_calibration`,
     `scenario_metrics`, `compare_scenarios`
   - actions: `run_simulation` (minutes), `optimize_signals` (tens of minutes;
     requires `confirm=true`), `render_report` (seconds)
   Durations and assumptions are stated in the tool docstrings.
3. **Safety:** area names validated against the registry; report outputs must
   resolve under `results/` or `docs/reports/`; signal files must live inside
   the repo; no network exposure (stdio only).
4. **Paths:** the server resolves the repo root from `__file__` and passes
   absolute roots to the pipeline, so behavior does not depend on the client's
   working directory.
5. **Testability:** plain module-level functions registered with
   `server.add_tool(...)` — the `@server.tool()` decorator reorders positional
   arguments by input schema, which would make direct unit calls surprising.
   Tests cover tool functions, an in-memory client round trip (list + call over
   `create_client_server_memory_streams`), and a stdio integration test marked
   `integration`.
6. **Cross-agent registration:** `rushlab` is added once to `agent/mcp.json`;
   `sync_agent_config.py` generates `opencode.json`, `.mcp.json`, and
   `.codex/config.toml`. Codex requires project trust; Claude Code prompts for
   MCP approval on first use (both documented in README).

## Consequences

- Long-running tools block the client during execution; the confirm gate on
  `optimize_signals` prevents accidental launches, and agents can schedule
  `run_simulation` deliberately.
- The MCP layer adds no new capability — it repackages the existing pipeline as
  a typed interface, keeping CLI and server behavior identical by construction
  (both call the same functions).
- Tool schema changes are a compatibility surface; the tool tests pin the
  expected tool names.
