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


