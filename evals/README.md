# RushLab benchmarks

Reproducible evidence for the agentic-development claims in this repo. Three
benchmarks, all run locally (they invoke paid agent CLIs and are excluded from
CI; CI tests only the parsing/counting code):

| Benchmark | Script | Agent calls | Typical time |
|---|---|---|---|
| Graphify token reduction | `graphify_tokens.py` | 0 (deterministic) + optional 1 | ~1 min |
| Plan vs execute A/B | `plan_vs_execute.py` | 4 | ~10-20 min |
| Skill efficacy | `skill_efficacy.py` | 2 | ~5-10 min |

## How to run

```bash
uv run python -m evals.graphify_tokens         # deterministic token accounting
uv run python -m evals.plan_vs_execute         # 2 tasks x 2 modes, opencode
uv run python -m evals.skill_efficacy          # release-notes skill, with/without
uv run python -m evals.summarize               # rebuild evals/RESULTS.md
```

Recorded results live in [`RESULTS.md`](RESULTS.md); raw tables and JSON under
`results/`. Scripts that import the shared harness must run as modules
(`python -m evals.…`) so the package resolves.

Common flags: `--cli opencode|claude|codex` (recorded numbers use `opencode`),
`--model provider/model` (defaults to the agent's configured model), `--timeout`.

## Honesty rules (also in ADR-0008)

- Recorded runs are **n=1** unless stated otherwise; every table names the CLI,
  model, and date. Single runs are indicative, not statistical.
- Agent benchmarks run against disposable copies under `evals/.work/` (gitignored);
  raw transcripts stay under `evals/transcripts/` (gitignored).
- Committed evidence is limited to `evals/results/*.json` and `evals/RESULTS.md`.
- The deterministic Graphify benchmark measures the token cost of the context an
  agent needs (tiktoken over the required files vs a `graphify query` answer),
  not an agent's actual context management.
- Nothing here claims real-world traffic outcomes; see `docs/decisions/`.
