# python-api-template

Personal template for Python API projects.

## What's included

- FastAPI app with a feature-based structure
- Configuration via `pydantic-settings`
- Health and readiness endpoints (`/health`, `/ready`)
- Structured JSON logging with request correlation (`request_id`) and service metadata
- RFC 9457 error responses with global exception handling
- CORS (default-closed) and browser security headers (HSTS in production)
- Production `Dockerfile` (slim, non-root)
- CI on GitHub Actions and Dependabot update checks
- Opinionated tooling: uv, Ruff, basedpyright, prek, pytest
- Decisions recorded as ADRs in [docs/adrs/](./docs/adrs/)

## Not included (yet)

Deliberately left to the adopter, tracked in [TODO.md](./TODO.md):

- Database, ORM, and migrations
- Authentication and authorization
- Rate limiting
- Observability (tracing and metrics, e.g. OpenTelemetry)
- A chosen HTTP client library
- Secret management strategy

## Tools

| Tool | Role | Config |
|------|------|--------|
| [uv](https://docs.astral.sh/uv/) | Package manager, virtualenv, Python version | `pyproject.toml` |
| [just](https://just.systems/) | Task runner | `Justfile` |
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework | — |
| [Ruff](https://docs.astral.sh/ruff/) | Linter and formatter | `pyproject.toml` `[tool.ruff]` |
| [basedpyright](https://docs.basedpyright.com/) | Type checker | `pyproject.toml` `[tool.basedpyright]` |
| [prek](https://github.com/j178/prek) | Pre-commit hooks (ruff + basedpyright) | `prek.toml` |
| [pytest](https://docs.pytest.org/) | Test runner (+ `pytest-cov` for coverage) | `pyproject.toml` `[tool.pytest.ini_options]` |
| [GitHub Actions](https://docs.github.com/actions) | CI (lint, format, types, tests) | `.github/workflows/ci.yml` |

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install [just](https://just.systems/man/en/installation.html).

## Setup

```bash
just setup
```

This installs dependencies and registers the pre-commit hooks.

## Running Commands

List available commands:

```bash
just --list
```

Activate the virtual environment before running project commands:

```bash
source .venv/bin/activate
```

## Testing

Tests live in `tests/`, split into two layers (`unit/` and `api/`). The full rationale,
TDD workflow, and per-layer responsibilities are documented in
[docs/standards/testing.md](./docs/standards/testing.md).

```bash
just test           # run the whole suite
just test-unit      # unit tests only
just test-api       # API (black box) tests only
just test-coverage  # whole suite with a term-missing coverage report
```

Coverage is measured against the `app` package via `pytest-cov`. The recipes treat
"no tests collected" (pytest exit code 5) as success, so an empty test directory does not
fail the run.

## CI/CD

Every pull request and every push to `main` runs lint, format, type-check, and tests on
GitHub Actions. The same `just` recipes run locally and in CI. See
[docs/ci-cd.md](./docs/ci-cd.md) for the goals, decisions, and cost-control measures.
