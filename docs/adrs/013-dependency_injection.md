# 013 — Dependency Injection: Provider-function chain

- **Decision**: One FastAPI provider function per layer in the feature's `dependencies.py`. Domain classes stay FastAPI-free.
- **Date**: 2026-06-13

## Problem

Where does FastAPI's `Depends()` stop and plain Python begin? Two common failures: `Depends()` inside service/repository constructors (couples domain to FastAPI), or hand-wiring the whole graph in every route handler (boilerplate in the HTTP layer).

## Rationale

- Domain classes take plain arguments, no `Depends` in their signatures, so they are unit-testable with no app.
- `dependencies.py` is the only FastAPI-aware module per feature: one provider per layer, each depending on the layer below.
- Routes depend only on the top of the chain (the service alias); FastAPI resolves the rest.
- Test seam is `app.dependency_overrides` at the needed altitude (infra for integration, service for handler tests), always cleared via a fixture.

## Rejected alternatives

- **`Depends()` in constructors**: makes domain classes unconstructible without FastAPI.
- **Instantiate the graph in the handler**: leaks construction into the HTTP boundary and repeats wiring per route.

## Consequences

- Each `dependencies.py` holds a provider plus an `Annotated[..., Depends(...)]` alias per layer.
- Infra providers (data source, db session, config) are the override seam; primary data stores are seeded with real state in black-box tests, not overridden.
- Supersedes the DI guidance in the FastAPI standard that forbade services in `Depends()` and prescribed handler-side instantiation.
