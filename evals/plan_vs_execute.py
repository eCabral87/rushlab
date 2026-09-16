"""Plan-vs-execute A/B benchmark on fixture tasks (local paid agent calls)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from evals.agent_runner import diff_stats, fresh_workdir, run_agent, snapshot

EVALS_DIR = Path(__file__).parent
TASKS_DIR = EVALS_DIR / "tasks"
RESULTS_DIR = EVALS_DIR / "results"
WORK_ROOT = EVALS_DIR / ".work"

PROMPTS = {
    "merge_intervals": (
        "Fix merge_ranges in src/interval_merge/merge.py so that every test in "
        "tests/test_merge.py passes. Run the tests to verify. Do not modify the tests."
    ),
    "slugify": (
        "Extend slugify in src/slugify/__init__.py so that every test in "
        "tests/test_slugify.py passes: fold unicode accents to ASCII and support an "
        "optional max_length that truncates at a word boundary without leaving a "
        "trailing hyphen. Run the tests to verify. Do not modify the tests."
    ),
}
PLAN_SUFFIX = "Produce a concise implementation plan (steps and edge cases). Do not modify files."


def tests_result(workdir: Path) -> dict:
    process = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=300,
    )
    passed_match = re.search(r"(\d+) passed", process.stdout)
    failed_match = re.search(r"(\d+) failed", process.stdout)
    tail = process.stdout.strip().splitlines()[-2:] if process.stdout else []
    return {
        "ok": process.returncode == 0,
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else 0,
        "tail": " | ".join(tail),
    }


def run_cell(task: str, mode: str, *, cli: str, model: str | None, timeout: float) -> dict:
    fixture = TASKS_DIR / task
    stamp = datetime.now(UTC).strftime("%H%M%S")
    workdir = fresh_workdir(fixture, WORK_ROOT, f"{task}-{mode}-{stamp}")
    before = snapshot(workdir)
    runs = []
    if mode == "direct":
        runs.append(
            run_agent(
                cli,
                PROMPTS[task],
                workdir=workdir,
                agent="build",
                model=model,
                timeout=timeout,
                transcript_name=f"{task}-{mode}-build",
            )
        )
    else:
        plan = run_agent(
            cli,
            f"{PROMPTS[task]}\n\n{PLAN_SUFFIX}",
            workdir=workdir,
            agent="plan",
            model=model,
            timeout=timeout,
            transcript_name=f"{task}-{mode}-plan",
        )
        runs.append(plan)
        follow_up = (
            f"{PROMPTS[task]}\n\nA plan was produced earlier in this task; follow it:\n\n"
            f"{plan.text[:6000]}"
        )
        runs.append(
            run_agent(
                cli,
                follow_up,
                workdir=workdir,
                agent="build",
                model=model,
                timeout=timeout,
                transcript_name=f"{task}-{mode}-build",
            )
        )
    after = snapshot(workdir)
    return {
        "task": task,
        "mode": mode,
        "cli": cli,
        "model": model,
        "workdir": str(workdir.relative_to(EVALS_DIR.parent)),
        "runs": [run.to_dict() for run in runs],
        "tokens_in": sum(run.tokens_in for run in runs),
        "tokens_out": sum(run.tokens_out for run in runs),
        "cost_usd": round(sum(run.cost_usd or 0 for run in runs), 6),
        "wall_s": round(sum(run.wall_s for run in runs), 1),
        "checks": tests_result(workdir),
        "diff": diff_stats(before, after),
    }


def render_markdown(result: dict) -> str:
    lines = [
        "## Plan vs execute (A/B)",
        "",
        f"CLI `{result['cli']}`, model `{result['model'] or 'configured default'}`, "
        f"generated {result['generated_at']}. n=1 per cell; treat as indicative, not statistical.",
        "",
        "| Task | Mode | Runs | Tokens in | Tokens out | Wall (s) | Tests | "
        "Files written | +/- lines |",
        "|---|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for cell in result["cells"]:
        checks = cell["checks"]
        tests = f"{checks['passed']} passed" + (
            f", {checks['failed']} failed" if checks["failed"] else ""
        )
        diff = cell["diff"]
        lines.append(
            f"| {cell['task']} | {cell['mode']} | {len(cell['runs'])} | "
            f"{cell['tokens_in']:,} | {cell['tokens_out']:,} | {cell['wall_s']} | {tests} | "
            f"{diff['files_written']} | +{diff['lines_added']}/-{diff['lines_removed']} |"
        )
    by_task: dict[str, dict[str, dict]] = {}
    for cell in result["cells"]:
        by_task.setdefault(cell["task"], {})[cell["mode"]] = cell
    lines += ["", "### Observations", ""]
    for task, modes in by_task.items():
        if "direct" in modes and "plan_first" in modes:
            direct, planned = modes["direct"], modes["plan_first"]
            direct_lines = direct["diff"]["lines_added"] + direct["diff"]["lines_removed"]
            planned_lines = planned["diff"]["lines_added"] + planned["diff"]["lines_removed"]
            lines.append(
                f"- **{task}**: direct {direct['tokens_in'] + direct['tokens_out']:,} tok / "
                f"{direct_lines} changed lines vs plan-first "
                f"{planned['tokens_in'] + planned['tokens_out']:,} tok / "
                f"{planned_lines} changed lines "
                f"(tests: {'pass' if direct['checks']['ok'] else 'fail'} vs "
                f"{'pass' if planned['checks']['ok'] else 'fail'})."
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", default="opencode", choices=["opencode", "claude", "codex"])
    parser.add_argument("--model", default=None, help="provider/model; default = configured")
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--tasks", default=",".join(PROMPTS), help="comma-separated task names")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    tasks = [task.strip() for task in args.tasks.split(",") if task.strip()]
    cells = []
    for task in tasks:
        for mode in ("direct", "plan_first"):
            print(f"running {task} [{mode}] via {args.cli} ...", flush=True)
            cells.append(run_cell(task, mode, cli=args.cli, model=args.model, timeout=args.timeout))
    result = {
        "benchmark": "plan_vs_execute",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "cli": args.cli,
        "model": args.model,
        "cells": cells,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "plan_vs_execute.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )
    markdown = render_markdown(result)
    (args.output_dir / "plan_vs_execute.md").write_text(markdown)
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
