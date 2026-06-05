# Application Structure — app-structure-05.06.2026-layers

Layer-based structure. Re-evaluate toward feature-based if the app grows beyond ~5 domains.

## Layout

```
app/
  routers/
  services/
  repositories/
  schemas/
  models/
  core/
```

## Layers

### `routers/`

HTTP boundary. One file per resource (e.g., `users.py`, `orders.py`).

- Route definitions, path/query parameter parsing
- Input: Pydantic schemas. Output: Pydantic schemas
- Calls services -- nothing else

Must not contain: business logic, SQL queries, ORM model construction.

### `services/`

Business logic. One file per domain.

- Orchestrates repositories and enforces domain rules
- Receives and returns Pydantic schemas or primitives
- No knowledge of HTTP (no `Request`, `Response`, status codes)

Must not contain: SQL queries, HTTP objects, direct ORM access.

### `repositories/`

Data access. One file per resource.

- All database queries live here, nowhere else
- Returns ORM models or primitives -- not schemas
- No business rules or validation logic

Must not contain: business logic, HTTP objects, Pydantic schemas.

### `schemas/`

Pydantic models for API input/output. One file per resource.

- Request bodies, response shapes, query parameter models
- May have `Base`, `Create`, `Update`, `Read` variants per resource

Must not contain: ORM relationships, SQLAlchemy types, business logic.

### `models/`

ORM table definitions. One file per resource or group of related tables.

- ORM model classes only -- pure data structure, no business logic

Must not contain: Pydantic schemas, business logic, HTTP concerns.

### `core/`

Shared infrastructure. Not feature-specific.

- `db.py` -- session factory, engine, base model class
- `config.py` -- settings (via Pydantic `BaseSettings`)
- `dependencies.py` -- shared FastAPI `Depends()` functions (db session, current user)
- `lifespan.py` -- app startup/shutdown (connection pools, HTTP clients)

Must not contain: feature-specific code, business logic, route definitions.
