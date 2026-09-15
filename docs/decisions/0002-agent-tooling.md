# 0002 — Agent-agnostic tooling layout

- Status: accepted
- Date: 2026-09-15

## Context

The repo must work with opencode, Claude Code, and Codex. Each tool uses
different project conventions:

| Concern | opencode | Claude Code | Codex |
|---|---|---|---|
| Instructions | `AGENTS.md` via `opencode.json` | `CLAUDE.md` | `AGENTS.md` |
| Skills | `.opencode/skills/` | `.claude/skills/` | `.agents/skills/` |
| MCP | `opencode.json` | `.mcp.json` | `.codex/config.toml` |
| Hooks | `.opencode/plugins/` | `.claude/settings.json` | `.codex/hooks.json` |

Maintaining four-plus copies by hand invites drift, and treating any one tool's
path as canonical privileges that tool.

## Decisions

1. **Neutral sources under `agent/`** — `agent/skills/`, `agent/mcp.json`,
   `agent/hooks.json`. No agent auto-reads these paths; they exist only as the
   single edit point.
2. **All per-tool files are generated** by `scripts/sync_agent_config.py` and
   checked in. `--check` mode fails CI on drift, so generated files cannot
   silently diverge.
3. **`AGENTS.md` stays canonical for instructions** because it is the cross-tool
   standard (native in opencode and Codex); `CLAUDE.md` is a shim importing it.
4. **MCP servers are defined once** in `agent/mcp.json` and translated into each
   tool's native format. Commands run from the project venv
   (`uv run --no-sync ...`), so no global installs are required.
5. **Session-start graph reminders use each tool's native hook** on top of one
   shared script (`scripts/graphify_reminder.py`): plain text for Claude Code,
   `hookSpecificOutput.additionalContext` JSON for Codex, and opencode's plugin.
6. **Temporary intentional asymmetry:** opencode's reminder is a vendored plugin
   (`graphify install` output) rather than generated; it is the only non-generated
   agent artifact and is documented in `agent/README.md`.

## Consequences

- Adding a skill = one file in `agent/skills/` + one sync command.
- Generated JSON files cannot carry "generated" comments; README and this ADR
  mark them, and the doctor/CI guard covers what comments would.
- Two trust prompts remain outside repo control and are documented in README:
  Codex project/hook trust and Claude Code workspace/MCP approval.
- `graphify-out/graph.json` and `GRAPH_REPORT.md` are committed so MCP works
  immediately after `uv sync`; `graph.html` and caches stay ignored.
