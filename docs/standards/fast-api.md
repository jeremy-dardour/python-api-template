# FastAPI

## Dependency Injection — fast-api-05.06.2026-DI

See [ADR 013](../adrs/013-dependency_injection.md) for the decision.

### Rule

One provider function per layer lives in the feature's `dependencies.py`. Each provider receives the layer below via `Depends()` and returns a built object. Domain classes (services, repositories) take plain arguments and never carry `Depends` in their signatures.

### Layering

```
Route          -> Depends(get_todo_service)
  get_todo_service(repository: TodoRepositoryDep)   # provider, FastAPI-aware
    get_todo_repository(csv_path: TodosCsvPathDep)  # provider, FastAPI-aware
      get_todos_csv_path()                          # infrastructure (db session, config, ...)
```

`TodoService` and `TodoRepository` themselves take plain arguments (a repository, a `Path`) and have no knowledge of FastAPI.

### Pattern

```python
# dependencies.py — the only FastAPI-aware module in the feature
def get_todos_csv_path() -> Path:
    return _TODOS_CSV_PATH
TodosCsvPathDep = Annotated[Path, Depends(get_todos_csv_path)]

def get_todo_repository(csv_path: TodosCsvPathDep) -> TodoRepository:
    return TodoRepository(csv_path)
TodoRepositoryDep = Annotated[TodoRepository, Depends(get_todo_repository)]

def get_todo_service(repository: TodoRepositoryDep) -> TodoService:
    return TodoService(repository)
TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]

# router.py — no construction
@router.get("")
async def get_todos(service: TodoServiceDep) -> list[TodoRead]:
    return await service.get_all()
```

### Rules

- Provider functions and their `Depends` aliases live in `dependencies.py`, one per layer.
- Service and repository classes take plain arguments; no `Depends` in their constructors.
- Infrastructure (db session, current user, config, request-scoped context) sits at the bottom of the chain and is the override seam for tests.
- Primary data stores are seeded with real state in black-box API tests, not overridden. Reserve `app.dependency_overrides` for external services and unit-level handler tests, always cleared via a fixture.

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
