# Testing Stack — testing-stack-2026-06-13

- **Decision**: pytest + pytest-asyncio + httpx.AsyncClient + pytest-mock + FastAPI dependency_overrides
- **Date**: 2026-06-13

## Problem

A FastAPI application requires three distinct testing concerns: unit testing of business logic in isolation, black-box HTTP-level testing of the API surface, and controlled mocking of dependencies injected via FastAPI's `Depends()` system. These concerns require different tools that must work coherently together in an async-first codebase.

## Alternatives considered

- **pytest** (~13.7k ★, used by 1.6M repositories) — test runner
- **pytest-asyncio** (~1.6k ★) — async test support
- **httpx** (~15.3k ★) — async HTTP client and ASGI test transport
- **pytest-mock** (~2k ★) — mock fixture wrapper
- **FastAPI `dependency_overrides`** — built-in DI override mechanism
- **unittest** — built-in test framework, no external dependency
- **requests + TestClient** — sync-only alternative for API testing
- **unittest.mock** — built-in mock library, no external dependency

## Rationale

- **pytest** is the de facto standard for Python testing. Its fixture system, assertion introspection, and plugin ecosystem have no credible competition.
- **pytest-asyncio** enables `async def test_...` functions natively, consistent with FastAPI's async-first model. Without it, async code must be wrapped in `asyncio.run()` at every test boundary.
- **httpx.AsyncClient** with the ASGI transport mounts the FastAPI app directly without spinning up a server. It covers both sync and async route handlers transparently at the HTTP protocol level, making a separate sync client redundant.
- **pytest-mock** provides a `mocker` fixture that wraps `unittest.mock`, integrates naturally with pytest's fixture lifecycle (automatic cleanup, no manual `patch.stop()`), and improves assertion failure messages via pytest introspection.
- **FastAPI `dependency_overrides`** is the purpose-built mechanism for replacing `Depends()` targets in tests. It requires no additional dependency and integrates with FastAPI's DI resolution directly.

## Rejected alternatives

- **unittest**: Verbose class-based structure; no fixture composition; no parametrize ergonomics. No reason to choose it over pytest on a greenfield project.
- **requests + TestClient**: Sync-only. Using it alongside async tests would require two client patterns in the same codebase. httpx.AsyncClient covers both.
- **unittest.mock directly**: Functionally equivalent to pytest-mock but requires manual `patcher.start()` / `patcher.stop()` lifecycle management. pytest-mock handles this via fixtures at no extra cost.

## Consequences

- `just test` runs `uv run pytest`.
- `just test-cov` runs pytest with coverage reporting.
- All test functions are `async def`; pytest-asyncio mode is set to `asyncio_mode = "auto"` in `pyproject.toml` to avoid decorating every test with `@pytest.mark.asyncio`.
- API tests use `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")` — no live server needed.
- Dependency injection is overridden per-test via `app.dependency_overrides` in fixtures, cleared in teardown.
- `mocker` fixture is used for patching callables outside FastAPI's DI system (external clients, utility functions, etc.).
- testing best practices are defined in [standards/testing](../standards/testing.md).

---