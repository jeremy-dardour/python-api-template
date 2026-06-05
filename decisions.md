# Decisions

Record of architectural and tooling choices made for this template.

---

## Package Management

- **Decision**: uv
- **Date**: 2026-06-05

**Alternatives considered**:
- `pip` + `requirements.txt` (+ pip-tools, virtualenv)
- Poetry
- PDM

**Rationale**:
- Significantly faster dependency resolution and installation, reducing local development and CI build times.
- Uses standard Python packaging (`pyproject.toml`) rather than introducing a proprietary project model.
- Provides dependency management, lockfiles, virtual environment management, and Python version management in a single tool.
- Produces reproducible environments through lockfiles committed to source control.
- Well-suited for containerized deployments where dependency installation speed directly impacts build times.
- Reduces the number of tools developers must learn and maintain.
- Growing adoption and ecosystem support make it a low-risk choice for new projects.

**Rejected alternatives**:
- **Poetry**: slower dependency resolution and an additional abstraction layer without sufficient benefits.
- **PDM**: fewer practical advantages over uv with a smaller ecosystem and community.
- **pip + requirements.txt**: requires combining multiple tools to achieve modern dependency management, locking, and environment reproducibility.

**Consequences**:
- Virtual environment management is handled via `uv venv` — no separate `virtualenv` or `venv` invocations needed.
- Python version management is handled via `uv python` — no separate `pyenv` needed.
- Dependency locking is handled via `uv.lock` — this file should be committed to source control for reproducible environments.

---

## Commit Format

- **Decision**: Conventional Commits
- **Date**: 2026-06-05

See [standard/commit-format.md](./standard/commit-format.md) for the full spec. The `/commit` project skill enforces it.

---

<!--
## [Topic]

- **Decision**: What was chosen
- **Date**: YYYY-MM-DD

**Alternatives considered**:
-

**Rationale**:
-

**Rejected alternatives**:
-

**Consequences**:
-
-->
