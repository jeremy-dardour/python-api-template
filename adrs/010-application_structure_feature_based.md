# 010 — Application Structure: Feature-based

- **Decision**: Feature-based (vertical slice) structure
- **Date**: 2026-06-13
- **Supersedes**: [003 — Application Structure: Layer-based](003-application_structure.md)

## Problem

The layer-based structure (ADR 003) organises code by technical concern: all routers in `routers/`, all services in `services/`, and so on. Adding or modifying a feature requires touching multiple top-level directories simultaneously. With a concrete domain (todos) in place, this becomes visible: a single feature spans `routers/todos.py`, `services/todos.py`, `repositories/todos.py`, `schemas/todos.py`, `models/todos.py`, and `core/dependencies/todos.py`. Navigation is by layer, not by feature.

## Rationale

- Colocating all files for a feature (router, service, repository, schemas, models, dependencies) reduces the cognitive cost of working on that feature end-to-end.
- Adding or removing a feature maps to adding or removing one directory — no cross-cutting changes across multiple top-level folders.
- The layer separation principle is preserved within each feature directory: the same "must not contain" rules still apply per file, they are just colocated.
- Shared infrastructure (`core/`) remains at the app level for concerns that are not feature-specific.

## Rejected alternatives

- **Keep layer-based**: Still the right choice for a genuinely blank-slate template with no domains. Rejected now that todos is a concrete reference domain that makes the cost of layer-based navigation visible.

## Structure

```
src/app/
  {feature}/
    router.py        # HTTP boundary — one router per feature
    service.py       # Business logic
    repository.py    # Data access
    schemas.py       # Pydantic request/response models
    models.py        # Domain models
    dependencies.py  # FastAPI Depends() wiring for this feature
  core/              # Shared infrastructure only (config, db, lifespan)
  main.py
```

## Consequences

- Each feature is a self-contained directory under `src/app/`.
- The layer rules from ADR 003 still apply within each file — only the directory grouping changes.
- `core/` is reserved for cross-cutting concerns; no feature-specific code lives there.
- Tests mirror this: `tests/api/test_{feature}.py`, `tests/unit/{feature}/test_{file}.py`.
