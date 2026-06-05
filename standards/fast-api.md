# FastAPI

## Dependency Injection — fast-api-05.06.2026-DI

### Rule

`Depends()` resolves infrastructure at the route boundary. Everything below is plain Python.

### Layering

```
Route
  └── Depends(get_db)               # infrastructure: db session, current user, config
  └── calls Service(db)
        └── calls Repository(db)    # plain constructor injection, no Depends()
```

Services and repositories are instantiated in the route handler (or via a plain factory function) and receive already-resolved resources as constructor arguments. They have no knowledge of FastAPI.

### Pattern

```python
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)
    return await service.get(user_id)
```

### What belongs in `Depends()`

- DB session
- Current authenticated user
- Config / settings
- Request-scoped infrastructure (feature flags, tenant context)

### What does not belong in `Depends()`

- Repositories
- Services
- Any domain logic

### Why

Pulling repositories and services into `Depends()` chains couples domain code to FastAPI. Testing then requires either manually calling the dependency chain or using `app.dependency_overrides` -- a global mutation on the app object that leaks between tests if not cleaned up. Plain constructor injection keeps domain code testable as regular Python.

### Singletons

Use the `lifespan` context manager to initialize shared resources once and attach to `app.state`. Dependencies read from there.

```python
@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.db_pool = await create_pool()
    application.state.http_client = AsyncClient()
    yield
    await application.state.db_pool.close()
    await application.state.http_client.aclose()
```

### Yield dependencies

Use only for resource lifecycle -- open, yield, close. No logic, no branching. Handle cleanup failures explicitly; they are swallowed silently by default.
