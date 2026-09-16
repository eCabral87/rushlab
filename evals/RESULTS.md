# RushLab benchmark results

Regenerate with `uv run python -m evals.graphify_tokens`, `uv run python -m evals.plan_vs_execute`, `uv run python -m evals.skill_efficacy`, then `uv run python -m evals.summarize`.

## Graphify token reduction

Encoding `o200k_base`, query budget 1200 tokens, generated 2026-09-16T18:41:26+00:00.

| Question | Files (tok) | Grep+read (tok, files) | Explain (tok) | Explain vs search | Query (tok) | Query vs search |
|---|---:|---:|---:|---:|---:|---:|
| graph-travel-time | 2,333 | 11,582 (6) | 641 | 94.5% | 1,138 | 90.2% |
| border-sink | 3,213 | 2,586 (2) | 441 | 82.9% | 1,145 | 55.7% |
| demand-pipeline | 3,249 | 7,551 (5) | 504 | 93.3% | 1,206 | 84.0% |
| calibration | 1,922 | 4,091 (4) | 412 | 89.9% | 1,207 | 70.5% |
| port-metering | 5,193 | 7,993 (5) | 789 | 90.1% | 1,145 | 85.7% |
| signal-optimization | 2,270 | 5,288 (5) | 759 | 85.6% | 3,713 | 29.8% |
| webster | 1,759 | 5,607 (5) | 546 | 90.3% | 1,168 | 79.2% |
| report-pipeline | 1,910 | 9,588 (6) | 578 | 94.0% | 1,118 | 88.3% |
| agent-config-sync | 1,817 | 3,130 (4) | 662 | 78.8% | 1,017 | 67.5% |
| mcp-server | 2,393 | 4,970 (4) | 486 | 90.2% | 1,171 | 76.4% |

**Focused retrieval (explain): 5,818 tokens vs 62,386 tokens for grep+read (90.7% reduction; median per question 90.2%).** Exploratory queries: 77.5% vs search. Symbols resolved by the graph: 20/20.

Search baseline = union of `grep -ril <keyword>` matched text files (raw exploration cost). Explain = `graphify explain <symbol>` output. Both sides tokenized with the same encoding; see ADR-0008.

_Provenance: recorded 2026-09-16T18:41:26+00:00; CLI `deterministic`; model `configured default`._

## Plan vs execute (A/B)

CLI `opencode`, model `configured default`, generated 2026-09-16T18:44:01+00:00. n=1 per cell; treat as indicative, not statistical.

| Task | Mode | Runs | Tokens in | Tokens out | Wall (s) | Tests | Files written | +/- lines |
|---|---|---:|---:|---:|---:|---|---:|---|
| merge_intervals | direct | 1 | 54,645 | 424 | 11.6 | 5 passed | 1 | +2/-2 |
| merge_intervals | plan_first | 2 | 99,074 | 1,662 | 25.4 | 5 passed | 1 | +3/-7 |
| slugify | direct | 1 | 70,170 | 1,225 | 15.3 | 5 passed | 1 | +20/-6 |
| slugify | plan_first | 2 | 114,389 | 2,379 | 28.4 | 5 passed | 1 | +28/-6 |

### Observations

- **merge_intervals**: direct 55,069 tok / 4 changed lines vs plan-first 100,736 tok / 10 changed lines (tests: pass vs pass).
- **slugify**: direct 71,395 tok / 26 changed lines vs plan-first 116,768 tok / 34 changed lines (tests: pass vs pass).

_Provenance: recorded 2026-09-16T18:44:01+00:00; CLI `opencode`; model `configured default`._

## Skill efficacy (release-notes)

CLI `opencode`, model `configured default`, generated 2026-09-16T18:44:34+00:00. n=1 per arm.

| Arm | Rubric | Version | Changelog section | Grouped | Content | Tokens in/out | Wall (s) |
|---|---:|---|---|---|---|---:|---:|
| with_skill | 4/4 | 0.2.0 | yes | yes | yes | 68,016/960 | 15.7 |
| without_skill | 3/4 | 0.2.0 | yes | no | yes | 36,607/664 | 9.3 |

Rubric: correct semver bump for a `feat` commit (minor), changelog section present, entry grouped (Added/Changed/Fixed), entry has human-readable content. The prompt is identical for both arms; only the skill's presence differs. See ADR-0008.

_Provenance: recorded 2026-09-16T18:44:34+00:00; CLI `opencode`; model `configured default`._

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
