# 009 — Pre-commit Hooks: prek

- **Decision**: prek
- **Date**: 2026-06-09

## Problem

Checks only prevent issues if they are actually run. Relying on developers to remember `just check-all` before every commit is unreliable -- checks get skipped under time pressure, and CI becomes the first line of defense instead of the last. By the time CI catches an error, a push has already happened and a pipeline is burning.

## Alternatives considered

- pre-commit (~13k ★, ~4M downloads/month)
- prek (~0.1k ★) -- chosen
- lefthook (~4k ★)
- husky (JS ecosystem, ~32k ★)

## Rationale

- prek is a drop-in alternative to pre-commit written and maintained by the author of uv's shell completions -- designed specifically for Python-first projects.
- Configuration in `prek.toml` mirrors pre-commit's `repos` format exactly; hooks from the pre-commit ecosystem work without modification.
- Installable as a Python package (`uv add --dev prek`) with no external runtime dependency, unlike pre-commit which requires its own environment management.
- Runs ruff and basedpyright hooks directly from their official pre-commit mirrors, ensuring hook versions stay in sync with the versions pinned in `pyproject.toml`.

## Rejected alternatives

- **pre-commit**: The reference tool for this pattern. Rejected because prek offers an identical interface with better fit in a uv-managed Python project (pure Python install, no separate virtualenv per hook runner).
- **lefthook**: Fast and language-agnostic, but runs arbitrary shell commands rather than the pre-commit hook ecosystem -- loses access to the official ruff and basedpyright hook mirrors.
- **husky**: Node.js ecosystem; no place in a pure Python project.

## Consequences

- `prek.toml` at the project root defines all hooks: `ruff-check --fix`, `ruff-format`, and `basedpyright` (full tree, not staged-only).
- Hooks must be installed once per clone via `just setup`.
- On every `git commit`, ruff auto-fixes and formats staged files, then basedpyright type-checks the full `src/` tree. The commit is blocked if any check fails.
- Because the pre-commit hook enforces all checks, running `just check-all` manually before committing is redundant.
