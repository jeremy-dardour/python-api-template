# 004 — API Framework: FastAPI

- **Decision**: FastAPI
- **Date**: 2026-06-05

## Problem

A Python REST API needs a framework to handle routing, request parsing, response serialization, and OpenAPI documentation. This choice determines the async model, validation approach, and ecosystem compatibility for the life of the project.

## Alternatives considered

- Litestar
- Django + Django Ninja
- Flask
- Starlette

## Rationale

- Native async-first design with full ASGI support -- no bolt-on async.
- OpenAPI generation and request validation via Pydantic are built-in, not assembled from plugins.
- Largest ecosystem among modern Python async frameworks; third-party library support is broad and stable.
- Lower adoption risk than newer alternatives for a template intended to stay usable across projects.

## Rejected alternatives

- **Litestar**: Stronger static typing, class-based views, and more explicit DI make it architecturally appealing. Rejected on ecosystem maturity -- the community, tooling, and third-party integration story is meaningfully smaller, which creates friction for a general-purpose template.
- **Django + Django Ninja**: Well-suited for data-centric apps; the full Django surface area is overhead for a generic API template.
- **Flask**: Mature but sync-first; assembling async support, validation, and OpenAPI requires maintaining additional infrastructure that FastAPI provides out of the box.
- **Starlette**: FastAPI is built on Starlette. Using it directly leaves too much infrastructure to assemble for a production-ready starter.

## Consequences

- **FastAPI** as the web framework.
- **Pydantic v2** for request/response validation, schema definition, and settings management. Pydantic v2 is a hard dependency of FastAPI ≥0.100; its v1→v2 migration was breaking -- treat Pydantic major upgrades carefully.
- **Uvicorn** as the ASGI server for local development and production.
- The `Depends()` dependency injection pattern is FastAPI-specific and non-obvious. Testing code that uses `Depends()` requires either FastAPI's `TestClient` or explicit override patterns -- design injection points with testability in mind.
- DI standards are defined in [standards/fast-api.md](../standards/fast-api.md) under tag `fast-api-05.06.2026-DI`.
