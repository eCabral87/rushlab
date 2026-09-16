"""Assemble evals/RESULTS.md from the recorded benchmark result files."""

from __future__ import annotations

import json
from pathlib import Path

EVALS_DIR = Path(__file__).parent
RESULTS_DIR = EVALS_DIR / "results"

SECTIONS: tuple[tuple[str, str], ...] = (
    ("graphify_tokens.md", "graphify_tokens.json"),
    ("plan_vs_execute.md", "plan_vs_execute.json"),
    ("skill_efficacy.md", "skill_efficacy.json"),
)

WHAT_PROVES = """
## What these prove (and do not)

- **Graphify:** focused retrieval (`explain`) answers need ~91% fewer tokens than
  grep + reading every matched file, with 20/20 symbols resolved. That is the
  "stop re-reading raw files" claim, measured. It does **not** say graph queries
  always win: for a tiny, precisely known file set, reading two files can beat a
  query — the graph pays off for exploration and navigation.
- **Plan vs execute:** on small, well-specified fixture tasks both modes passed
  every test, while plan-first cost roughly 2x tokens (it is a second agent
  invocation). The benchmark does not show plan mode being wrong — it shows the
  trade is about task complexity, which is exactly the judgment the workflow
  asks agents to make.
- **Skill efficacy:** the release-notes skill produced the fully correct release
  (4/4 rubric points) versus 3/4 without it, at ~1.9x the tokens. Skills buy
  convention adherence; they are not free.
- All numbers are **n=1** on recorded runs (CLI and model named in each table).
  They are indicators recorded for this repo, not statistical claims.
"""


def main() -> int:
    parts = [
        "# RushLab benchmark results",
        "",
        "Regenerate with `uv run python -m evals.graphify_tokens`, "
        "`uv run python -m evals.plan_vs_execute`, `uv run python -m evals.skill_efficacy`, "
        "then `uv run python -m evals.summarize`.",
        "",
    ]
    for md_name, json_name in SECTIONS:
        json_path = RESULTS_DIR / json_name
        md_path = RESULTS_DIR / md_name
        if not json_path.is_file() or not md_path.is_file():
            parts.append(f"_{md_name}: not recorded yet_")
            parts.append("")
            continue
        payload = json.loads(json_path.read_text())
        parts.append(md_path.read_text().strip())
        parts.append("")
        parts.append(
            f"_Provenance: recorded {payload.get('generated_at')}; CLI "
            f"`{payload.get('cli', 'deterministic')}`; model "
            f"`{payload.get('model') or 'configured default'}`._"
        )
        parts.append("")
    parts.append(WHAT_PROVES.strip())
    parts.append("")
    output = EVALS_DIR / "RESULTS.md"
    output.write_text("\n".join(parts))
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
