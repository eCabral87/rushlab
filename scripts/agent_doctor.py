#!/usr/bin/env python3
"""Verify the agent setup: generated files, config parsing, and graph presence.

Usage:
    uv run python scripts/agent_doctor.py
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from sync_agent_config import build_outputs  # noqa: E402

GENERATED = (
    "opencode.json",
    ".mcp.json",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".claude/settings.json",
)

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def main() -> int:
    outputs = build_outputs()

    drift = [
        str(path.relative_to(ROOT))
        for path, text in outputs.items()
        if not path.is_file() or path.read_text() != text
    ]
    check("generated files match agent/ sources", not drift, ", ".join(drift))

    for relative in GENERATED:
        path = ROOT / relative
        ok = path.is_file()
        detail = "" if ok else "missing"
        if ok:
            try:
                text = path.read_text()
                if relative.endswith(".toml"):
                    tomllib.loads(text)
                else:
                    json.loads(text)
            except (ValueError, tomllib.TOMLDecodeError) as exc:
                ok, detail = False, str(exc)
        check(f"{relative} parses", ok, detail)

    check(
        "graphify reminder script present",
        (ROOT / "scripts" / "graphify_reminder.py").is_file(),
    )
    check(
        "knowledge graph present",
        (ROOT / "graphify-out" / "graph.json").is_file(),
        "run: uv run graphify update .",
    )

    failures = 0
    for name, ok, detail in results:
        status = "ok  " if ok else "FAIL"
        suffix = f" ({detail})" if detail and not ok else ""
        print(f"[{status}] {name}{suffix}")
        if not ok:
            failures += 1

    if failures:
        print(f"\n{failures} check(s) failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
