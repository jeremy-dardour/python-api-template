# 2026-06-09 Linter and Formatter: Ruff

- **Decision**: Ruff (for both linting and formatting)
- **Date**: 2026-06-09

## Alternatives considered

- Flake8 + Black + isort
- Pylint + Black + isort

## Rationale

- Single tool replaces Flake8, isort, and Black, eliminating version and configuration conflicts between tools.
- Significantly faster than any Python-based linter/formatter combination -- written in Rust.
- Configuration lives entirely in `pyproject.toml` under `[tool.ruff]` alongside other project metadata.
- `ruff check --fix` and `ruff format` cover the full lint-and-format workflow in two commands.
- Active development and growing ecosystem support make it a stable long-term choice.

## Rejected alternatives

- **Flake8 + Black + isort**: Three tools to configure and keep compatible; slower; no auto-fix for many lint rules.
- **Pylint + Black + isort**: Pylint's analysis is deeper but significantly slower and noisier; the same three-tool coordination problem applies.

## Consequences

- `just lint` / `just lint-fix` for checking and auto-fixing lint violations.
- `just format-check` / `just format` for checking and applying formatting.
- `just check-all` and `just fix-all` run both in sequence.
- Rule selection in `[tool.ruff.lint]` pins the active rule sets -- additions should be deliberate and reviewed.
