# Decisions

Record of architectural and tooling choices made for this template.
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

See [standards/commit-format.md](./standards/commit-format.md) for the full spec. The `/commit` project skill enforces it.

---

## API Framework

- **Decision**: FastAPI
- **Date**: 2026-06-05

**Alternatives considered**:
- Litestar
- Django + Django Ninja
- Flask
- Starlette

**Rationale**:
- Native async-first design with full ASGI support -- no bolt-on async.
- OpenAPI generation and request validation via Pydantic are built-in, not assembled from plugins.
- Largest ecosystem among modern Python async frameworks; third-party library support is broad and stable.
- Lower adoption risk than newer alternatives for a template intended to stay usable across projects.

**Rejected alternatives**:
- **Litestar**: Stronger static typing, class-based views, and more explicit DI make it architecturally appealing. Rejected on ecosystem maturity -- the community, tooling, and third-party integration story is meaningfully smaller, which creates friction for a general-purpose template.
- **Django + Django Ninja**: Well-suited for data-centric apps; the full Django surface area is overhead for a generic API template.
- **Flask**: Mature but sync-first; assembling async support, validation, and OpenAPI requires maintaining additional infrastructure that FastAPI provides out of the box.
- **Starlette**: FastAPI is built on Starlette. Using it directly leaves too much infrastructure to assemble for a production-ready starter.

**Consequences**:
- **FastAPI** as the web framework.
- **Pydantic v2** for request/response validation, schema definition, and settings management. Pydantic v2 is a hard dependency of FastAPI ≥0.100; its v1→v2 migration was breaking -- treat Pydantic major upgrades carefully.
- **Uvicorn** as the ASGI server for local development and production.
- The `Depends()` dependency injection pattern is FastAPI-specific and non-obvious. Testing code that uses `Depends()` requires either FastAPI's `TestClient` or explicit override patterns -- design injection points with testability in mind.
- DI standards are defined in [standards/fast-api.md](./standards/fast-api.md) under tag `fast-api-05.06.2026-DI`.

---

## Task Runner

- **Decision**: just (Justfile)
- **Date**: 2026-06-09

**Alternatives considered**:
- `make` / Makefile
- Plain shell scripts

**Rationale**:
- Simpler syntax than Makefile with no footgun tab-vs-space issues and no implicit POSIX shell behaviors.
- Cross-platform (macOS, Linux, Windows via WSL) without additional tooling.
- Commands are self-documenting via `just --list`.
- Works well alongside uv -- recipes are thin wrappers around `uv run` commands, keeping the task runner and package manager cleanly separated.

**Rejected alternatives**:
- **Makefile**: Ubiquitous but designed for build dependency graphs, not developer scripts. Tab-indentation requirement and implicit rules are frequent sources of confusion.
- **Shell scripts**: No discoverability; each developer must read the script or documentation to know what's available.

**Consequences**:
- `just dev` starts the development server with hot-reload.
- `just start` starts the production server.
- New developer tasks should be added as `just` recipes in the `Justfile`.

---

## Linter and Formatter

- **Decision**: Ruff (for both linting and formatting)
- **Date**: 2026-06-09

**Alternatives considered**:
- Flake8 + Black + isort
- Pylint + Black + isort

**Rationale**:
- Single tool replaces Flake8, isort, and Black, eliminating version and configuration conflicts between tools.
- Significantly faster than any Python-based linter/formatter combination -- written in Rust.
- Configuration lives entirely in `pyproject.toml` under `[tool.ruff]` alongside other project metadata.
- `ruff check --fix` and `ruff format` cover the full lint-and-format workflow in two commands.
- Active development and growing ecosystem support make it a stable long-term choice.

**Rejected alternatives**:
- **Flake8 + Black + isort**: Three tools to configure and keep compatible; slower; no auto-fix for many lint rules.
- **Pylint + Black + isort**: Pylint's analysis is deeper but significantly slower and noisier; the same three-tool coordination problem applies.

**Consequences**:
- `just lint` / `just lint-fix` for checking and auto-fixing lint violations.
- `just format-check` / `just format` for checking and applying formatting.
- `just check-all` and `just fix-all` run both in sequence.
- Rule selection in `[tool.ruff.lint]` pins the active rule sets -- additions should be deliberate and reviewed.

---

## Type Checker

- **Decision**: basedpyright
- **Date**: 2026-06-09

**Alternatives considered**:
- mypy (~20.5k ★)
- pyright (~15.5k ★)
- basedpyright (~3.4k ★) ← chosen
- ty, by Astral (~18.8k ★) ← deferred


**Rationale**:
- FastAPI and Pydantic v2 are designed and tested against pyright's type system — their generics, stubs, and inference patterns are tuned for it. basedpyright inherits this compatibility directly.
- pip-installable (`uv add --dev basedpyright`) with no Node.js dependency, unlike upstream pyright — cleaner Docker builds and CI pipelines.
- Stricter defaults than pyright out of the box: catches more issues without manual `strict` flag configuration.
- Tracks pyright releases closely (last release was 4 days behind pyright 1.1.410), so it is not a stale fork.
- Configuration lives in `pyproject.toml` under `[tool.basedpyright]`, consistent with the rest of the toolchain.

**Rejected alternatives**:
- **mypy** (~20.5k ★): Still the most widely adopted type checker and has the broadest plugin ecosystem, but its Pydantic v2 support lags behind pyright, it is significantly slower, and the "use mypy for SQLAlchemy" argument is largely legacy — SQLAlchemy 2.0 ships with native pyright stubs.
- **pyright** (~15.5k ★): The upstream tool basedpyright is forked from. Functionally equivalent but requires Node.js as a runtime dependency, which is an unnecessary footgun in a pure Python project. basedpyright is a strict superset in terms of checks.
- **ty** (~18.8k ★): Written in Rust by Astral (the creators of uv and ruff), 10–100x faster than mypy/pyright, and architecturally aligned with the rest of this toolchain. However, it is currently versioned at `0.0.x` and explicitly does not guarantee stability between releases — breaking diagnostic changes can occur on any update. Type system coverage also has known gaps tracked in an open

**Consequences**:
- `just typecheck` runs `basedpyright` against the source tree.
- Type checking mode is set to "strict" from project initialization. Exceptions for third-party libraries with incomplete stubs are handled per-package via [tool.basedpyright.overrides] rather than by downgrading the global mode.
- If a library is added with significantly better mypy support and no pyright stubs (rare, but possible), this decision should be revisited. Switching is low-cost — it's a dev-only tool with no runtime impact.
- `[tool.basedpyright]` block in `pyproject.toml` configures `pythonVersion`, `pythonPlatform`, and `venvPath`.

---


