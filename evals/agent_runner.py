"""Headless agent runners and usage parsers for the benchmarks.

Recorded benchmark numbers use opencode; the Claude Code and Codex adapters are
best-effort and their parsers are unit-tested against synthetic event samples.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TRANSCRIPTS_DIR = Path(__file__).parent / "transcripts"


@dataclass
class RunResult:
    cli: str
    prompt: str
    wall_s: float
    exit_code: int
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float | None = None
    session_id: str | None = None
    text: str = ""
    steps: int = 0
    stderr_tail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "cli": self.cli,
            "prompt": self.prompt,
            "wall_s": self.wall_s,
            "exit_code": self.exit_code,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost_usd": self.cost_usd,
            "session_id": self.session_id,
            "steps": self.steps,
            "text_chars": len(self.text),
        }


def _find_token_usage(payload: Any) -> dict[str, Any] | None:
    """Recursively find a dict carrying input/output token counts."""
    if isinstance(payload, dict):
        if "input_tokens" in payload or "output_tokens" in payload:
            return payload
        for key in ("usage", "payload", "msg", "info"):
            if key in payload:
                found = _find_token_usage(payload[key])
                if found:
                    return found
        return None
    if isinstance(payload, list):
        for item in payload:
            found = _find_token_usage(item)
            if found:
                return found
    return None


def parse_opencode_events(lines: list[str]) -> dict[str, Any]:
    """Sum usage across step_finish events; collect assistant text."""
    tokens_in = tokens_out = steps = 0
    cost = 0.0
    session_id: str | None = None
    texts: list[str] = []
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        session_id = event.get("sessionID") or session_id
        part = event.get("part") or {}
        if event.get("type") == "text" and part.get("type") == "text":
            texts.append(str(part.get("text", "")))
        if event.get("type") == "step_finish":
            usage = part.get("tokens") or {}
            cache = usage.get("cache") or {}
            tokens_in += int(usage.get("input", 0))
            tokens_in += int(cache.get("read", 0)) + int(cache.get("write", 0))
            tokens_out += int(usage.get("output", 0)) + int(usage.get("reasoning", 0))
            cost += float(part.get("cost") or 0.0)
            steps += 1
    return {
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": round(cost, 6),
        "session_id": session_id,
        "text": "\n".join(text for text in texts if text),
        "steps": steps,
    }


def parse_claude_result(stdout: str) -> dict[str, Any]:
    payload = json.loads(stdout)
    usage = payload.get("usage") or {}
    tokens_in = int(usage.get("input_tokens", 0))
    tokens_in += int(usage.get("cache_creation_input_tokens") or 0)
    tokens_in += int(usage.get("cache_read_input_tokens") or 0)
    return {
        "tokens_in": tokens_in,
        "tokens_out": int(usage.get("output_tokens", 0)),
        "cost_usd": payload.get("total_cost_usd"),
        "session_id": payload.get("session_id"),
        "text": str(payload.get("result", "")),
        "steps": int(payload.get("num_turns", 0) or 0),
    }


def parse_codex_events(lines: list[str]) -> dict[str, Any]:
    """Best-effort: take the largest cumulative usage found in JSONL events."""
    tokens_in = tokens_out = 0
    texts: list[str] = []
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = _find_token_usage(event)
        if usage:
            tokens_in = max(tokens_in, int(usage.get("input_tokens", 0)))
            tokens_in += int(usage.get("cached_input_tokens", 0) or 0)
            tokens_out = max(
                tokens_out,
                int(usage.get("output_tokens", 0))
                + int(usage.get("reasoning_output_tokens", 0) or 0),
            )
        payload = event.get("payload") or event
        if isinstance(payload, dict) and payload.get("type") in ("agent_message", "text"):
            texts.append(str(payload.get("message", payload.get("text", ""))))
    return {
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": None,
        "session_id": None,
        "text": "\n".join(text for text in texts if text),
        "steps": 0,
    }


def _write_transcript(name: str, stdout: str, stderr: str) -> None:
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    (TRANSCRIPTS_DIR / f"{name}.stdout").write_text(stdout)
    (TRANSCRIPTS_DIR / f"{name}.stderr").write_text(stderr[-4000:])


def run_opencode(
    prompt: str,
    *,
    workdir: Path,
    agent: str | None = None,
    model: str | None = None,
    auto: bool = True,
    timeout: float = 900.0,
    transcript_name: str | None = None,
) -> RunResult:
    command = ["opencode", "run", "--format", "json", "--dir", str(workdir)]
    if agent:
        command += ["--agent", agent]
    if model:
        command += ["-m", model]
    if auto:
        command.append("--auto")
    command.append(prompt)
    started = time.monotonic()
    process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    wall = time.monotonic() - started
    parsed = parse_opencode_events(process.stdout.splitlines())
    if transcript_name:
        _write_transcript(transcript_name, process.stdout, process.stderr)
    return RunResult(
        cli="opencode",
        prompt=prompt,
        wall_s=round(wall, 1),
        exit_code=process.returncode,
        stderr_tail=process.stderr[-500:],
        **parsed,
    )


def run_claude(
    prompt: str,
    *,
    workdir: Path,
    model: str | None = None,
    allowed_tools: str = "Read,Edit,Write,Bash",
    timeout: float = 900.0,
    transcript_name: str | None = None,
) -> RunResult:
    command = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "json",
        "--allowedTools",
        allowed_tools,
        "--permission-mode",
        "acceptEdits",
    ]
    if model:
        command += ["--model", model]
    started = time.monotonic()
    process = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=workdir)
    wall = time.monotonic() - started
    parsed = parse_claude_result(process.stdout)
    if transcript_name:
        _write_transcript(transcript_name, process.stdout, process.stderr)
    return RunResult(
        cli="claude",
        prompt=prompt,
        wall_s=round(wall, 1),
        exit_code=process.returncode,
        stderr_tail=process.stderr[-500:],
        **parsed,
    )


def run_codex(
    prompt: str,
    *,
    workdir: Path,
    model: str | None = None,
    timeout: float = 900.0,
    transcript_name: str | None = None,
) -> RunResult:
    command = [
        "codex",
        "exec",
        "--json",
        "--cd",
        str(workdir),
        "--sandbox",
        "workspace-write",
        prompt,
    ]
    if model:
        command += ["--model", model]
    started = time.monotonic()
    process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    wall = time.monotonic() - started
    parsed = parse_codex_events(process.stdout.splitlines())
    if transcript_name:
        _write_transcript(transcript_name, process.stdout, process.stderr)
    return RunResult(
        cli="codex",
        prompt=prompt,
        wall_s=round(wall, 1),
        exit_code=process.returncode,
        stderr_tail=process.stderr[-500:],
        **parsed,
    )


RUNNERS = {"opencode": run_opencode, "claude": run_claude, "codex": run_codex}


def run_agent(cli: str, prompt: str, **kwargs: Any) -> RunResult:
    if cli not in RUNNERS:
        raise ValueError(f"unknown cli {cli!r}; choose from {sorted(RUNNERS)}")
    return RUNNERS[cli](prompt, **kwargs)


def snapshot(
    directory: Path, *, ignore: tuple[str, ...] = (".git", "__pycache__")
) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or any(part in ignore for part in path.parts):
            continue
        files[str(path.relative_to(directory))] = path.read_text(errors="replace")
    return files


def diff_stats(before: dict[str, str], after: dict[str, str]) -> dict[str, int]:
    added = removed = 0
    for name, content in after.items():
        if name not in before:
            added += len(content.splitlines())
            continue
        if before[name] != content:
            import difflib

            for line in difflib.unified_diff(
                before[name].splitlines(), content.splitlines(), lineterm=""
            ):
                if line.startswith("+") and not line.startswith("+++"):
                    added += 1
                elif line.startswith("-") and not line.startswith("---"):
                    removed += 1
    for name, content in before.items():
        if name not in after:
            removed += len(content.splitlines())
    return {
        "files_written": sum(1 for name in after if before.get(name) != after[name]),
        "files_deleted": sum(1 for name in before if name not in after),
        "lines_added": added,
        "lines_removed": removed,
    }


def fresh_workdir(fixture: Path, work_root: Path, name: str) -> Path:
    target = work_root / name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(fixture, target)
    return target
