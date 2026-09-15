#!/usr/bin/env python3
"""Keep agent skill mirrors in sync with the canonical opencode skills.

Canonical: .opencode/skill/<name>/SKILL.md
Mirrors:   .claude/skills/<name>/SKILL.md   (Claude Code)
           .agents/skills/<name>/SKILL.md   (cross-tool convention, Codex)

Usage:
    uv run python scripts/sync_agent_config.py          # write mirrors
    uv run python scripts/sync_agent_config.py --check  # exit 1 if stale (CI)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / ".opencode" / "skill"
MIRRORS = (
    ROOT / ".claude" / "skills",
    ROOT / ".agents" / "skills",
)
SKILL_FILE = "SKILL.md"


def canonical_skills() -> dict[str, Path]:
    skills = {}
    if CANONICAL.is_dir():
        for child in sorted(CANONICAL.iterdir()):
            skill_file = child / SKILL_FILE
            if skill_file.is_file():
                skills[child.name] = skill_file
    return skills


def mirror_skills(mirror: Path) -> dict[str, Path]:
    skills = {}
    if mirror.is_dir():
        for child in sorted(mirror.iterdir()):
            skill_file = child / SKILL_FILE
            if skill_file.is_file():
                skills[child.name] = skill_file
    return skills


def sync(check: bool) -> int:
    canonical = canonical_skills()
    if not canonical:
        print(f"error: no skills found under {CANONICAL}", file=sys.stderr)
        return 1

    stale: list[str] = []
    for mirror in MIRRORS:
        existing = mirror_skills(mirror)
        for name, source in canonical.items():
            target = mirror / name / SKILL_FILE
            source_text = source.read_text()
            if not target.is_file() or target.read_text() != source_text:
                stale.append(f"{target.relative_to(ROOT)}")
                if not check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(source_text)
        for name, target in existing.items():
            if name not in canonical:
                stale.append(f"{target.relative_to(ROOT)} (orphan)")
                if not check:
                    target.unlink()

    if check and stale:
        print("Agent skill mirrors are stale:")
        for path in stale:
            print(f"  {path}")
        print("Run: uv run python scripts/sync_agent_config.py")
        return 1

    action = "checked" if check else "synced"
    mirrors = ", ".join(str(m.relative_to(ROOT)) for m in MIRRORS)
    print(f"{action} {len(canonical)} skill(s) -> {mirrors}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify mirrors without writing")
    args = parser.parse_args()
    return sync(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
