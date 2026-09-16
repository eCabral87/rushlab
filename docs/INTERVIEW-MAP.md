# Interview evidence map

Every CV line below maps to committed artifacts you can open during the
interview, a 60-second talking point, the most likely follow-up question, the
honest limit, and a command to verify the claim live.

**Quick stats:** 10 commits, 98 tests, 8 ADRs (`docs/decisions/`), CI green,
one-page study report, three recorded benchmarks. Everything except live data
fetches works offline from committed caches.

| CV line | Status | Evidence |
|---|---|---|
| Agentic AI workflows | Strong | `AGENTS.md`, commit history, `evals/RESULTS.md`. 1 |
| Agent skills & tools | Strong | `agent/skills/` (3), `rushlab-mcp` (8 tools). 2 |
| Plan vs execute | Strong | `AGENTS.md` rule 1, ADR-0008, benchmark. 3 |
| Knowledge-graph workflows | Strong | `graphify-out/graph.json`, token benchmark. 4 |
| LLM tooling fluency | Strong | `agent/` + generated configs, doctor/CI drift check. 5 |
| ML/DL/DSP (audio, sensors) | Not this project | covered by other experience. 6 |
| Optimization / graph theory | Strong | Webster+GA, min-cut, centrality. 7 |
| Telecom / wireless | Not this project | covered by other experience. 8 |

---

## 1. Agentic AI — designing and orchestrating multi-step workflows

**Artifacts:** `AGENTS.md` (working rules), `docs/decisions/0003–0008`
(decisions taken *by* agents under a written policy), `evals/plan_vs_execute.py`
and `evals/results/plan_vs_execute.json`.

**60-second talking point:** "The whole project was built agent-first: every
feature landed through a written workflow — plan before code over ~30 LOC, TDD,
small conventional commits, assumptions documented in ADRs. The pipeline itself,
eight days of work, is the orchestration evidence: OSM ingestion → calibration →
SUMO → optimization → report, each stage driven by an agent under review. I also
measured the workflow: two fixture tasks with tests, run direct vs plan-first
(`evals/RESULTS.md`)."

**Likely question:** "What did the agents get wrong?" — Answer with the real
examples: the Jinja `dict.values` regression (`90a4a13`), the netconvert
`--tls.set` + `--tllogic-files` ordering trap, and the initial 858-gateway
network that forced the main-road filter. All caught by tests or review.

**Honest limit:** process discipline is enforced by written policy and CI, not by
tool-enforced sandboxes.

**Verify:** `uv run python scripts/agent_doctor.py` · `git log --oneline`

## 2. Agent skills & tools

**Artifacts:** `agent/skills/{add-study-area,run-scenario-study,release-notes}`,
`src/rushlab/mcp_server.py` (8 tools), `.opencode/`, `.claude/`, `.codex/`
generated configs.

**60-second talking point:** "Skills are real working documents, not demos:
`run-scenario-study` encodes the exact baseline/scenario/report procedure this
repo uses, and `release-notes` is the procedure that produced this changelog.
On top, the repo ships its own MCP server with eight typed tools — analysis,
calibration, simulation, optimization, report rendering — registered once and
generated for opencode, Claude Code, and Codex. I measured skill impact: the
release-notes skill scored 4/4 on a scripted rubric versus 3/4 without it."

**Likely question:** "Why do you generate three configs?" — One neutral source
(`agent/`) prevents drift; CI fails when generated files diverge; Codex/Claude
each require their own native format.

**Honest limit:** agent runs are nondeterministic; the skill benchmark is n=1.

**Verify:** `ls agent/skills` · `uv run python scripts/sync_agent_config.py --check`

## 3. Plan vs execute modes

**Artifacts:** `AGENTS.md` rule 1, `evals/plan_vs_execute.py`,
`docs/decisions/0008-benchmark-methodology.md`.

**60-second talking point:** "I treat plan mode as a cost decision, and I
measured it. Two fixture tasks with failing tests, four agent runs: both modes
passed every test, but plan-first cost roughly twice the tokens (55k → 101k on
the merge task, 71k → 117k on the feature task) because it is a second agent
invocation. So the judgment is: plan when scope is ambiguous or multi-file;
execute directly on small, well-specified changes — and say why."

**Likely question:** "When would planning have won?" — Multi-file refactors,
unclear requirements, risky migrations; my fixtures are deliberately small so the
benchmark is honest about what it shows.

**Honest limit:** n=1 per cell, one model, two small tasks.

**Verify:** `uv run python -m evals.plan_vs_execute` (paid runs) or read
`evals/results/plan_vs_execute.md`

## 4. Knowledge-graph workflows (Graphify)

**Artifacts:** `graphify-out/graph.json` + `GRAPH_REPORT.md` (committed),
`.opencode/plugins/graphify.js`, reminder hooks in `.claude/settings.json` and
`.codex/hooks.json`, `evals/graphify_tokens.py`.

**60-second talking point:** "The repo indexes itself into a knowledge graph, and
agents query it instead of grepping: ten real architecture questions measured
with tiktoken — focused `graphify explain` answers cost 5,818 tokens versus
62,386 for grep-and-read, a 90.7% reduction, with 20/20 symbols resolved. I also
found and documented the honest boundary: if you already know the two files, a
query can cost more; the graph pays off for exploration."

**Likely question:** "Where does the graph get stale?" — It is rebuilt with
`graphify update .` and committed; CI/doctor check presence, and I note that the
committed graph is a snapshot (regeneration is one command).

**Honest limit:** token benchmark measures required context, not an agent's
actual context management.

**Verify:** `uv run --no-sync graphify explain metering_program` ·
`evals/RESULTS.md`

## 5. LLM tooling fluency (IDE and CLI)

**Artifacts:** `agent/mcp.json`, `agent/hooks.json`, generated `opencode.json`,
`.mcp.json`, `.codex/config.toml`, `.claude/settings.json`,
`scripts/sync_agent_config.py`, `scripts/agent_doctor.py`, CI workflow.

**60-second talking point:** "I run opencode, Claude Code, and Codex from one
project definition. Skills, MCP servers, and session hooks live once under
`agent/`; a sync script generates each tool's native files, CI fails on drift,
and a doctor script verifies the whole setup. That is day-to-day fluency:
headless runs, JSON event parsing for token accounting, MCP stdio debugging, and
hooks per tool."

**Likely question:** "Show me a cross-tool difference you had to handle." —
Claude Code needs `CLAUDE.md` importing `AGENTS.md` and project-scope `.mcp.json`;
Codex uses `.agents/skills` + project-trusted `.codex/config.toml`; opencode
reads `AGENTS.md` plus `.opencode/`.

**Verify:** `uv run python scripts/agent_doctor.py` · `cat agent/mcp.json`

## 6. ML / DL / DSP (audio, sensors) — not this project

This project was deliberately traffic-domain (per a scoping decision), so it does
**not** evidence the audio/sensor CV line. Say so plainly and point to the other
experience: `Eval_SQA_SpeechModels` (speech-quality assessment with neural MOS
metrics, VAD preprocessing, published tooling) and the course material in
`ai-engineering-from-scratch` phases 01–12.

## 7. Optimization and graph theory

**Artifacts:** `src/rushlab/network/metrics.py` (betweenness, articulation
points, bridges, min-cut with capacity proxies), `src/rushlab/signals/webster.py`
(Webster cycle/splits), `src/rushlab/signals/optimizer.py` (DEAP GA over
offsets), `docs/reports/san-ysidro-signal-optimization.html`.

**60-second talking point:** "Graph theory does real work here: betweenness plus
articulation/bridge analysis ranks the corridor's critical intersections, and
min-cut against the capacity proxy finds the capacity into the border. The
optimization side is Webster for cycle and splits, then a genetic algorithm over
green-wave offsets evaluated by simulation — 166 evaluations in the recorded
run. The finding matters more than the machinery: the metered port dominates, so
retiming upstream signals moved throughput only +3.5%."

**Likely question:** "Why didn't you use an ILP for survivable design?" — I kept
capacity analysis structural (min-cut) because calibrated demand was thin; I
would add an ILP (PuLP/HiGHS) once lane-level counts exist, and note that the
GA-vs-Webster split mirrors what practitioners do.

**Honest limit:** capacity proxy is lanes × 1800 veh/h, not operational capacity.

**Verify:** `uv run rushlab analyze san-ysidro --top 10 --no-calibrated` ·
`docs/decisions/0006-signal-optimization.md`

## 8. Telecom / wireless — not this project

Also outside this project's scope by design. Cover it from prior experience (and
offer the transferable framing: networks as graphs, capacity, resilience,
routing — the same math with different edge semantics). If pressed, the honest
line is: "This project shows graph/optimization depth; my telecom depth comes
from X."

---

## How to use this map

1. Skim the table; pick the three strongest lines and rehearse their talking
   points with a timer.
2. Run the verify commands once before the interview so the caches are warm.
3. For gaps, state them in one sentence and pivot to the evidence you do have —
   interviewers reward calibration, not over-claiming.
