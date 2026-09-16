# 0008 — Benchmark methodology

- Status: accepted
- Date: 2026-09-16

## Context

The project claims agentic-development benefits (knowledge-graph context, plan
mode, skills). Those claims need recorded evidence that is honest, reproducible,
and cheap to re-run. Three benchmarks cover the claims; this ADR fixes their
methodology and limits.

## Decisions

1. **Deterministic token benchmark** (`evals/graphify_tokens.py`): for ten real
   architecture questions, compare three costs tokenized with tiktoken
   (`o200k_base`):
   - `files`: curated source files a reader must open (floor),
   - `search`: union of `grep -ril <keyword>` matched text files (raw
     exploration cost),
   - `explain`: `graphify explain <symbol>` output per symbol (focused retrieval),
   - `query`: `graphify query --budget 1200` (exploratory retrieval).
   Budgets above ~1500 make the traversal dump many nodes (observed 13k tokens at
   a 4000 budget), so 1200 is fixed for comparability.
2. **Plan-vs-execute A/B** (`evals/plan_vs_execute.py`): two self-contained
   fixture tasks in disposable copies; direct = one `--agent build` run,
   plan-first = `--agent plan` followed by `--agent build` with the plan
   attached. Metrics: tokens, wall time, tests passing, files/lines changed.
3. **Skill efficacy** (`evals/skill_efficacy.py`): a mini repo with a real
   `feat` commit; the same prompt runs with the canonical `release-notes` skill
   copied in and with it removed. A scripted rubric (semver bump, changelog
   section, grouping, content) scores the outcome.
4. **Harness** (`evals/agent_runner.py`): adapters for opencode (recorded),
   Claude Code and Codex (parsers unit-tested, best-effort). Token accounting
   for opencode sums `step_finish` events; model is recorded per run and defaults
   to the agent's configured model.
5. **CI policy:** agent benchmarks are local-only (cost, auth, flakiness). CI
   runs unit tests for parsers, token counting, rubrics, and snapshot/diff math
   only. `evals/.work/` and `evals/transcripts/` are gitignored; committed
   evidence is `evals/results/*.json`, `evals/results/*.md`, and `evals/RESULTS.md`.

## Recorded results (2026-09-16, opencode, configured default model)

- **Graphify:** explain 5,818 tokens vs 62,386 tokens for grep+read across the
  ten questions — **90.7% fewer tokens**, median 90.2%, 20/20 symbols resolved;
  exploratory queries 77.5% below the search baseline.
- **Plan vs execute:** 4/4 cells passed their tests; plan-first used ~2x tokens
  and changed slightly more lines on these small tasks (55k vs 101k tokens on
  merge_intervals; 71k vs 117k on slugify).
- **Skill efficacy:** with skill 4/4 rubric points at 68k tokens; without skill
  3/4 (missing changelog grouping) at 37k tokens.

## Honest limits

- All recorded numbers are **n=1**; they are indicators, not statistics. The
  harness supports repetitions (`n>1` by re-running), and tables state the sample.
- The token benchmark measures required context, not an agent's actual context
  management; an agent may read more or less than the measured baseline.
- Agent runs are nondeterministic; fixture tasks are small on purpose so results
  are comparable and cheap to reproduce.
- No benchmark speaks to traffic outcomes; those claims live in ADRs 0001-0007.
