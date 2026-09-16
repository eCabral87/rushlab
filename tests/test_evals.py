"""Eval-harness parsing and math tests. No agent calls, no subprocesses."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals import agent_runner
from evals.graphify_tokens import count_tokens, keyword_hits, naive_context_tokens, render_markdown

OPENCODE_EVENTS = "\n".join(
    [
        json.dumps({"type": "step_start", "sessionID": "ses_1", "part": {"type": "step-start"}}),
        json.dumps(
            {
                "type": "text",
                "sessionID": "ses_1",
                "part": {"type": "text", "text": "first"},
            }
        ),
        json.dumps(
            {
                "type": "step_finish",
                "sessionID": "ses_1",
                "part": {
                    "type": "step-finish",
                    "tokens": {
                        "input": 100,
                        "output": 10,
                        "reasoning": 5,
                        "cache": {"read": 1000, "write": 200},
                    },
                    "cost": 0.01,
                },
            }
        ),
        json.dumps(
            {
                "type": "text",
                "sessionID": "ses_1",
                "part": {"type": "text", "text": "second"},
            }
        ),
        json.dumps(
            {
                "type": "step_finish",
                "sessionID": "ses_1",
                "part": {
                    "type": "step-finish",
                    "tokens": {"input": 50, "output": 5, "cache": {"read": 0, "write": 0}},
                    "cost": 0.005,
                },
            }
        ),
    ]
).splitlines()


def test_parse_opencode_events_sums_steps() -> None:
    parsed = agent_runner.parse_opencode_events(OPENCODE_EVENTS)
    assert parsed["tokens_in"] == 100 + 1000 + 200 + 50
    assert parsed["tokens_out"] == 10 + 5 + 5
    assert parsed["cost_usd"] == pytest.approx(0.015)
    assert parsed["session_id"] == "ses_1"
    assert parsed["text"] == "first\nsecond"
    assert parsed["steps"] == 2


def test_parse_claude_result() -> None:
    stdout = json.dumps(
        {
            "usage": {
                "input_tokens": 100,
                "output_tokens": 20,
                "cache_creation_input_tokens": 300,
                "cache_read_input_tokens": 4000,
            },
            "total_cost_usd": 0.02,
            "session_id": "abc",
            "result": "done",
            "num_turns": 3,
        }
    )
    parsed = agent_runner.parse_claude_result(stdout)
    assert parsed["tokens_in"] == 4400
    assert parsed["tokens_out"] == 20
    assert parsed["cost_usd"] == pytest.approx(0.02)
    assert parsed["steps"] == 3


def test_parse_codex_events_takes_cumulative_max() -> None:
    lines = [
        json.dumps({"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 10}}),
        json.dumps(
            {
                "type": "turn.completed",
                "usage": {"input_tokens": 900, "output_tokens": 40, "cached_input_tokens": 50},
            }
        ),
    ]
    parsed = agent_runner.parse_codex_events(lines)
    assert parsed["tokens_in"] == 950
    assert parsed["tokens_out"] == 40


def test_snapshot_and_diff_stats(tmp_path: Path) -> None:
    target = tmp_path / "proj"
    target.mkdir()
    (target / "a.py").write_text("one\n")
    before = agent_runner.snapshot(target)
    (target / "a.py").write_text("one\ntwo\n")
    (target / "b.py").write_text("new\n")
    after = agent_runner.snapshot(target)
    stats = agent_runner.diff_stats(before, after)
    assert stats == {
        "files_written": 2,
        "files_deleted": 0,
        "lines_added": 2,
        "lines_removed": 0,
    }


def test_naive_context_tokens_and_missing(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("hello world")
    total, missing = naive_context_tokens(["a.md", "missing.md"], root=tmp_path)
    assert total == count_tokens("hello world")
    assert missing == ["missing.md"]


def test_keyword_hits_case_insensitive() -> None:
    assert keyword_hits("The Sink_Capacity is set", ["sink_capacity", "absent"]) == [
        "sink_capacity"
    ]


def test_render_markdown_contains_totals() -> None:
    result = {
        "benchmark": "graphify_token_reduction",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "encoding": "o200k_base",
        "query_budget": 1200,
        "rows": [
            {
                "id": "q1",
                "question": "?",
                "files_tokens": 1000,
                "missing_files": [],
                "search_files": ["a.py", "b.py"],
                "search_tokens": 4000,
                "explain_tokens": 600,
                "explain_details": [{"symbol": "s", "tokens": 600, "found": True}],
                "explain_vs_search_pct": 85.0,
                "explain_vs_files_pct": 40.0,
                "query_tokens": 1300,
                "query_vs_search_pct": 67.5,
                "symbols_found": 1,
                "symbols_total": 1,
            }
        ],
        "aggregate": {
            "questions": 1,
            "symbols_found": 1,
            "symbols_total": 1,
            "explain_vs_search_pct_total": 85.0,
            "query_vs_search_pct_total": 67.5,
            "explain_vs_search_pct_median": 85.0,
            "query_vs_search_pct_median": 67.5,
            "files_tokens_total": 1000,
            "search_tokens_total": 4000,
            "explain_tokens_total": 600,
            "query_tokens_total": 1300,
        },
    }
    markdown = render_markdown(result)
    assert "85.0% reduction" in markdown
    assert "q1" in markdown


def test_questions_file_is_valid() -> None:
    import yaml

    from evals.graphify_tokens import QUESTIONS_PATH

    entries = yaml.safe_load(QUESTIONS_PATH.read_text())["questions"]
    assert len(entries) >= 8
    for entry in entries:
        assert entry["question"] and entry["files"] and entry["symbols"] and entry["grep"]
