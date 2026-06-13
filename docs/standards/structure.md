# Application Structure

## Layout

```
src/
  app/
    {feature}/
      router.py        # HTTP boundary
      service.py       # Business logic
      repository.py    # Data access
      schemas.py       # Pydantic request/response models
      models.py        # Domain models
      dependencies.py  # FastAPI Depends() wiring for this feature
    core/              # Shared infrastructure only
    main.py
```

See [adrs/005-package_layout.md](../adrs/005-package_layout.md) for the rationale behind `src/`.
See [adrs/010-application_structure_feature_based.md](../adrs/010-application_structure_feature_based.md) for the rationale behind the feature-based structure.

## Feature directory

Each feature is a self-contained directory. All files for a domain live together.

Not every file is required — a simple feature may only need `router.py`. Add files as the feature grows.

### `router.py`

HTTP boundary. One router per feature.

- Route definitions, path/query parameter parsing
- Input: Pydantic schemas. Output: Pydantic schemas
- Calls services — nothing else

Must not contain: business logic, SQL queries, ORM model construction.

### `service.py`

Business logic.

- Orchestrates repositories and enforces domain rules
- Receives and returns Pydantic schemas or primitives
- No knowledge of HTTP (no `Request`, `Response`, status codes)

Must not contain: SQL queries, HTTP objects, direct ORM access.

### `repository.py`

Data access.

- All database queries live here, nowhere else
- Returns domain models or primitives — not schemas
- No business rules or validation logic

Must not contain: business logic, HTTP objects, Pydantic schemas.

### `schemas.py`

Pydantic models for API input/output.

- Request bodies, response shapes, query parameter models
- May have `Base`, `Create`, `Update`, `Read` variants per resource

Must not contain: ORM relationships, SQLAlchemy types, business logic.

### `models.py`

Domain model classes — pure data structure, no business logic.

Must not contain: Pydantic schemas, business logic, HTTP concerns.

### `dependencies.py`

FastAPI `Depends()` wiring scoped to this feature. One provider function per layer, each depending on the layer below, plus its `Annotated[..., Depends(...)]` alias. The only FastAPI-aware module in the feature. See [adrs/013-dependency_injection.md](../adrs/013-dependency_injection.md).

Must not contain: business logic, cross-feature dependencies.

## `core/`

Shared infrastructure. Not feature-specific.

- `db.py` — session factory, engine, base model class
- `config.py` — settings (via Pydantic `BaseSettings`)
- `dependencies.py` — shared `Depends()` functions (db session, current user)
- `lifespan.py` — app startup/shutdown (connection pools, HTTP clients)

Must not contain: feature-specific code, business logic, route definitions.
