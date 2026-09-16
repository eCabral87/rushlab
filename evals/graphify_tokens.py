"""Deterministic Graphify benchmark: graph context vs re-reading raw files.

Three measurements per question (all tokenized with tiktoken, o200k_base):

1. ``files``   - the curated source files a reader must open (floor).
2. ``search``  - ``grep -ril <keyword>`` matched files (what raw exploration costs).
3. ``explain`` - ``graphify explain <symbol>`` per symbol (focused retrieval).
   ``query``   - ``graphify query --budget 1200`` (exploratory retrieval).

Budgets above ~1500 tokens make the traversal dump many nodes; 1200 keeps the
answer scoped. See ADR-0008 for what this does and does not prove.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import tiktoken
import yaml

EVALS_DIR = Path(__file__).parent
REPO_ROOT = EVALS_DIR.parent
QUESTIONS_PATH = EVALS_DIR / "questions.yaml"
RESULTS_DIR = EVALS_DIR / "results"
ENCODING_NAME = "o200k_base"
QUERY_BUDGET = 1200
SEARCH_ROOTS = ("src", "tests", "scripts", "evals", "agent")
TEXT_SUFFIXES = (".py", ".md", ".yaml", ".yml", ".toml", ".j2", ".json", ".js", ".cfg")


def count_tokens(text: str) -> int:
    return len(tiktoken.get_encoding(ENCODING_NAME).encode(text))


def naive_context_tokens(files: list[str], root: Path = REPO_ROOT) -> tuple[int, list[str]]:
    total = 0
    missing: list[str] = []
    for relative in files:
        path = root / relative
        if not path.is_file():
            missing.append(relative)
            continue
        total += count_tokens(path.read_text(errors="replace"))
    return total, missing


def search_files(keyword: str, root: Path = REPO_ROOT) -> list[str]:
    process = subprocess.run(
        ["grep", "-ril", keyword, *SEARCH_ROOTS],
        cwd=root,
        capture_output=True,
        text=True,
    )
    files: list[str] = []
    for line in process.stdout.splitlines():
        path = root / line.strip()
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            path.read_text()
        except UnicodeDecodeError:
            continue
        files.append(line.strip())
    return sorted(files)


def search_tokens(files: list[str], root: Path = REPO_ROOT) -> int:
    return sum(count_tokens((root / name).read_text(errors="replace")) for name in files)


def graphify_explain(symbol: str, *, timeout: float = 120.0) -> str:
    """Explain a symbol; ambiguous or unknown symbols yield the raw output."""
    process = subprocess.run(
        ["uv", "run", "--no-sync", "graphify", "explain", symbol],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if process.returncode != 0 and not process.stdout.strip():
        raise RuntimeError(f"graphify explain failed: {process.stderr[-400:]}")
    return process.stdout


def graphify_query(question: str, *, budget: int = QUERY_BUDGET, timeout: float = 180.0) -> str:
    process = subprocess.run(
        ["uv", "run", "--no-sync", "graphify", "query", question, "--budget", str(budget)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if process.returncode != 0:
        raise RuntimeError(f"graphify query failed: {process.stderr[-400:]}")
    return process.stdout


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    return sorted(keyword for keyword in keywords if keyword.lower() in lowered)


def run(questions_path: Path = QUESTIONS_PATH, *, query_budget: int = QUERY_BUDGET) -> dict:
    entries = yaml.safe_load(questions_path.read_text())["questions"]
    rows: list[dict] = []
    for entry in entries:
        file_tokens, missing = naive_context_tokens(entry["files"])
        matched = search_files(entry["grep"])
        search_total = search_tokens(matched)
        explain_details = []
        explain_total = 0
        for symbol in entry["symbols"]:
            answer = graphify_explain(symbol)
            tokens = count_tokens(answer)
            explain_total += tokens
            explain_details.append({"symbol": symbol, "tokens": tokens, "found": "Node:" in answer})
        query_answer = graphify_query(entry["question"], budget=query_budget)
        query_total = count_tokens(query_answer)
        rows.append(
            {
                "id": entry["id"],
                "question": entry["question"],
                "files_tokens": file_tokens,
                "missing_files": missing,
                "search_files": matched,
                "search_tokens": search_total,
                "explain_tokens": explain_total,
                "explain_details": explain_details,
                "explain_vs_search_pct": round(100.0 * (1 - explain_total / search_total), 1)
                if search_total
                else None,
                "explain_vs_files_pct": round(100.0 * (1 - explain_total / file_tokens), 1)
                if file_tokens
                else None,
                "query_tokens": query_total,
                "query_vs_search_pct": round(100.0 * (1 - query_total / search_total), 1)
                if search_total
                else None,
                "symbols_found": sum(1 for item in explain_details if item["found"]),
                "symbols_total": len(entry["symbols"]),
            }
        )

    def median(key: str) -> float | None:
        values = [row[key] for row in rows if row[key] is not None]
        return round(statistics.median(values), 1) if values else None

    totals = {
        "files_tokens_total": sum(row["files_tokens"] for row in rows),
        "search_tokens_total": sum(row["search_tokens"] for row in rows),
        "explain_tokens_total": sum(row["explain_tokens"] for row in rows),
        "query_tokens_total": sum(row["query_tokens"] for row in rows),
    }
    aggregate = {
        "questions": len(rows),
        "symbols_found": sum(row["symbols_found"] for row in rows),
        "symbols_total": sum(row["symbols_total"] for row in rows),
        "explain_vs_search_pct_total": round(
            100.0 * (1 - totals["explain_tokens_total"] / totals["search_tokens_total"]), 1
        )
        if totals["search_tokens_total"]
        else None,
        "query_vs_search_pct_total": round(
            100.0 * (1 - totals["query_tokens_total"] / totals["search_tokens_total"]), 1
        )
        if totals["search_tokens_total"]
        else None,
        "explain_vs_search_pct_median": median("explain_vs_search_pct"),
        "query_vs_search_pct_median": median("query_vs_search_pct"),
        **totals,
    }
    return {
        "benchmark": "graphify_token_reduction",
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "encoding": ENCODING_NAME,
        "query_budget": query_budget,
        "rows": rows,
        "aggregate": aggregate,
    }


def render_markdown(result: dict) -> str:
    aggregate = result["aggregate"]
    lines = [
        "## Graphify token reduction",
        "",
        f"Encoding `{result['encoding']}`, query budget {result['query_budget']} tokens, "
        f"generated {result['generated_at']}.",
        "",
        "| Question | Files (tok) | Grep+read (tok, files) | Explain (tok) | "
        "Explain vs search | Query (tok) | Query vs search |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["rows"]:
        lines.append(
            f"| {row['id']} | {row['files_tokens']:,} | {row['search_tokens']:,} "
            f"({len(row['search_files'])}) | {row['explain_tokens']:,} | "
            f"{row['explain_vs_search_pct']}% | {row['query_tokens']:,} | "
            f"{row['query_vs_search_pct']}% |"
        )
    lines += [
        "",
        f"**Focused retrieval (explain): {aggregate['explain_tokens_total']:,} tokens vs "
        f"{aggregate['search_tokens_total']:,} tokens for grep+read "
        f"({aggregate['explain_vs_search_pct_total']}% reduction; median per question "
        f"{aggregate['explain_vs_search_pct_median']}%).** "
        f"Exploratory queries: {aggregate['query_vs_search_pct_total']}% vs search. "
        f"Symbols resolved by the graph: "
        f"{aggregate['symbols_found']}/{aggregate['symbols_total']}.",
        "",
        "Search baseline = union of `grep -ril <keyword>` matched text files (raw "
        "exploration cost). Explain = `graphify explain <symbol>` output. Both sides "
        "tokenized with the same encoding; see ADR-0008.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-budget", type=int, default=QUERY_BUDGET)
    parser.add_argument("--questions", type=Path, default=QUESTIONS_PATH)
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    args = parser.parse_args()

    result = run(args.questions, query_budget=args.query_budget)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "graphify_tokens.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )
    markdown = render_markdown(result)
    (args.output_dir / "graphify_tokens.md").write_text(markdown)
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
