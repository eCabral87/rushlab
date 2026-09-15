#!/usr/bin/env python3
"""Print a knowledge-graph hint when graphify-out/graph.json exists.

Used by agent session-start hooks:
  Claude Code: plain text on stdout becomes session context.
  Codex:       --format codex emits hookSpecificOutput.additionalContext JSON.

Silent (exit 0, no output) when the graph is absent so fresh clones stay quiet.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REMINDER = (
    "[graphify] Knowledge graph available at graphify-out/. "
    'For focused questions run: uv run --no-sync graphify query "<question>" '
    "(small scoped subgraph) instead of grepping raw files. "
    "Read graphify-out/GRAPH_REPORT.md for broad architecture context. "
    "The graphify MCP server exposes query_graph, get_node, get_neighbors, "
    "god_nodes, graph_stats, and shortest_path."
)


def project_root() -> Path:
    """Resolve the git top-level, falling back to the repo layout."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return Path(__file__).resolve().parent.parent
    return Path(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=("text", "codex"),
        default="text",
        help="text for Claude Code, codex for Codex hookSpecificOutput JSON",
    )
    args = parser.parse_args()

    if not (project_root() / "graphify-out" / "graph.json").is_file():
        return 0

    if args.format == "codex":
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": REMINDER,
            }
        }
        print(json.dumps(payload))
    else:
        print(REMINDER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
