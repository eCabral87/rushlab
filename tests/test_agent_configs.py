"""Generated agent configuration must stay valid and in sync."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def test_opencode_config_has_instructions_and_mcp() -> None:
    config = load_json("opencode.json")
    assert config["instructions"] == ["AGENTS.md"]
    graphify = config["mcp"]["graphify"]
    assert graphify["type"] == "local"
    assert graphify["command"][:3] == ["uv", "run", "--no-sync"]


def test_rushlab_mcp_registered_in_every_agent_config() -> None:
    opencode = load_json("opencode.json")
    assert opencode["mcp"]["rushlab"]["command"][:3] == ["uv", "run", "--no-sync"]
    assert opencode["mcp"]["rushlab"]["command"][-1] == "rushlab-mcp"
    claude = load_json(".mcp.json")
    assert claude["mcpServers"]["rushlab"]["args"][-1] == "rushlab-mcp"
    codex = tomllib.loads((ROOT / ".codex" / "config.toml").read_text())
    assert codex["mcp_servers"]["rushlab"]["args"][-1] == "rushlab-mcp"


def test_claude_mcp_config() -> None:
    config = load_json(".mcp.json")
    assert config["mcpServers"]["graphify"]["command"] == "uv"


def test_codex_config_parses_with_mcp() -> None:
    config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text())
    assert config["mcp_servers"]["graphify"]["command"] == "uv"


def test_session_start_hooks_exist() -> None:
    claude = load_json(".claude/settings.json")
    assert claude["hooks"]["SessionStart"]
    codex = load_json(".codex/hooks.json")
    assert codex["hooks"]["SessionStart"]


def test_skill_mirrors_cover_agent_sources() -> None:
    names = sorted(p.name for p in (ROOT / "agent" / "skills").iterdir() if p.is_dir())
    assert names
    for mirror in (".opencode/skills", ".claude/skills", ".agents/skills"):
        for name in names:
            assert (ROOT / mirror / name / "SKILL.md").is_file()


def test_agent_sources_parse() -> None:
    servers = load_json("agent/mcp.json")["servers"]
    assert servers["graphify"]["command"] == "uv"
    hooks = load_json("agent/hooks.json")
    assert hooks["session_start"]["script"] == "scripts/graphify_reminder.py"
