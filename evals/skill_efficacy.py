"""Skill-efficacy benchmark: release-notes skill with vs without."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from evals.agent_runner import diff_stats, fresh_workdir, run_agent, snapshot

EVALS_DIR = Path(__file__).parent
FIXTURE = EVALS_DIR / "tasks" / "release_notes"
CANONICAL_SKILL = EVALS_DIR.parent / "agent" / "skills" / "release-notes"
RESULTS_DIR = EVALS_DIR / "results"
WORK_ROOT = EVALS_DIR / ".work"

PROMPT = (
    "Prepare release v0.2.0 for this project: bump the version and add the changelog "
    "entry you consider appropriate. Update only pyproject.toml and CHANGELOG.md. "
    "Do not create tags or push."
)


def prepare(workdir: Path, *, with_skill: bool) -> None:
    if with_skill:
        skills_dir = workdir / ".opencode" / "skills" / "release-notes"
        skills_dir.mkdir(parents=True)
        shutil.copy(CANONICAL_SKILL / "SKILL.md", skills_dir / "SKILL.md")
    git = ["git", "-c", "user.email=bench@example.com", "-c", "user.name=bench"]
    subprocess.run([*git, "init", "-q"], cwd=workdir, check=True)
    subprocess.run([*git, "add", "-A"], cwd=workdir, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "chore: initial import"], cwd=workdir, check=True)
    init_file = workdir / "src" / "mini" / "__init__.py"
    init_file.write_text(
        init_file.read_text() + '\n\ndef greeting(name: str) -> str:\n    return f"hi {name}"\n'
    )
    subprocess.run([*git, "add", "src/mini/__init__.py"], cwd=workdir, check=True)
    subprocess.run(
        [*git, "commit", "-q", "-m", "feat: add greeting helper"], cwd=workdir, check=True
    )


def score_release(workdir: Path) -> dict:
    version = tomllib.loads((workdir / "pyproject.toml").read_text())["project"]["version"]
    changelog = (workdir / "CHANGELOG.md").read_text()
    has_section = bool(re.search(r"^##\s*v0\.2\.0", changelog, re.M))
    has_group = bool(re.search(r"^###?\s*(Added|Changed|Fixed)", changelog, re.M))
    section = re.search(r"^##\s*v0\.2\.0(.*?)(?=^##\s|\Z)", changelog, re.M | re.S)
    has_content = bool(section and re.search(r"^\s*[-*]\s+\S.{9,}", section.group(1), re.M))
    details = {
        "version_correct_minor": version == "0.2.0",
        "changelog_section": has_section,
        "changelog_grouped": has_group,
        "changelog_content": has_content,
    }
    return {
        "points": sum(1 for value in details.values() if value),
        "max_points": len(details),
        "version": version,
        "details": details,
    }


def render_markdown(result: dict) -> str:
    lines = [
        "## Skill efficacy (release-notes)",
        "",
        f"CLI `{result['cli']}`, model `{result['model'] or 'configured default'}`, "
        f"generated {result['generated_at']}. n=1 per arm.",
        "",
        "| Arm | Rubric | Version | Changelog section | Grouped | Content | "
        "Tokens in/out | Wall (s) |",
        "|---|---:|---|---|---|---|---:|---:|",
    ]
    for arm in result["arms"]:
        score = arm["score"]
        details = score["details"]
        lines.append(
            f"| {arm['arm']} | {score['points']}/{score['max_points']} | {score['version']} | "
            f"{'yes' if details['changelog_section'] else 'no'} | "
            f"{'yes' if details['changelog_grouped'] else 'no'} | "
            f"{'yes' if details['changelog_content'] else 'no'} | "
            f"{arm['tokens_in']:,}/{arm['tokens_out']:,} | {arm['wall_s']} |"
        )
    lines += [
        "",
        "Rubric: correct semver bump for a `feat` commit (minor), changelog section present, "
        "entry grouped (Added/Changed/Fixed), entry has human-readable content. The prompt is "
        "identical for both arms; only the skill's presence differs. See ADR-0008.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", default="opencode", choices=["opencode", "claude", "codex"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    arms = []
    for with_skill in (True, False):
        arm_name = "with_skill" if with_skill else "without_skill"
        print(f"running {arm_name} via {args.cli} ...", flush=True)
        stamp = datetime.now(UTC).strftime("%H%M%S")
        workdir = fresh_workdir(FIXTURE, WORK_ROOT, f"release-notes-{arm_name}-{stamp}")
        prepare(workdir, with_skill=with_skill)
        before = snapshot(workdir)
        run = run_agent(
            args.cli,
            PROMPT,
            workdir=workdir,
            agent="build",
            model=args.model,
            timeout=args.timeout,
            transcript_name=f"release-notes-{arm_name}",
        )
        after = snapshot(workdir)
        arms.append(
            {
                "arm": arm_name,
                "runs": [run.to_dict()],
                "tokens_in": run.tokens_in,
                "tokens_out": run.tokens_out,
                "cost_usd": run.cost_usd,
                "wall_s": run.wall_s,
                "score": score_release(workdir),
                "diff": diff_stats(before, after),
            }
        )
    result = {
        "benchmark": "skill_efficacy",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "cli": args.cli,
        "model": args.model,
        "arms": arms,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "skill_efficacy.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )
    markdown = render_markdown(result)
    (args.output_dir / "skill_efficacy.md").write_text(markdown)
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
