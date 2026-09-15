# Agent sources

Neutral, tool-agnostic definitions for every supported coding agent. This
directory is the single source of truth — never edit the generated files.

| Source | Generated |
|---|---|
| `skills/<name>/SKILL.md` | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` |
| `mcp.json` | `opencode.json`, `.mcp.json`, `.codex/config.toml` |
| `hooks.json` | `.claude/settings.json`, `.codex/hooks.json` |

opencode also keeps its native hook plugin at `.opencode/plugins/graphify.js`;
the reminder script it duplicates lives at `scripts/graphify_reminder.py`.

After editing any source:

```bash
uv run python scripts/sync_agent_config.py   # regenerate
uv run python scripts/agent_doctor.py        # verify
```

CI fails when generated files drift from these sources.
