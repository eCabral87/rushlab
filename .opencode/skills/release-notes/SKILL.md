---
name: release-notes
description: Use when preparing a RushLab release: version bump, changelog, tag, and GitHub release. Trigger keywords: release, bump version, changelog, tag, publish.
---

# Release Notes and Versioning

## Goal

Cut a clean release with a changelog that matches the actual commits.

## Procedure

1. **Check the tree.** `git status` must be clean and CI green on `main`.

2. **Bump the version** in `pyproject.toml` (semver):
   - `feat:` commits since last tag → minor
   - `fix:`/`perf:` only → patch
   - breaking CLI or config changes → major

3. **Write the changelog entry** in `CHANGELOG.md`:
   - Group: Added / Changed / Fixed / Removed
   - Link to the PR or commit for each bullet
   - Include benchmark deltas when the release changes agent behavior
     (Graphify tokens, scenario runtime)

4. **Verify the release locally.**
   ```bash
   uv sync --extra dev
   uv run ruff check . && uv run pyright && uv run pytest
   uv run rushlab --version
   ```

5. **Tag and release.**
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main --tags
   gh release create vX.Y.Z --notes-file <(awk '/^## vX.Y.Z/{flag=1;next}/^## v/{flag=0}flag' CHANGELOG.md)
   ```

## Rules

- The changelog is written for the release, never auto-generated from raw commits.
- No release with failing benchmarks: re-run `evals/` before tagging when agent
  configuration changed.
- Every release notes the study areas and data vintages it was validated against.
