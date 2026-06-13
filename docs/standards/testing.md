# FastAPI Testing Best Practices

## Structure

```
tests/
  conftest.py             # shared fixtures (client, db session, factories)
  unit/                   # mirrors the feature structure
    {feature}/
      test_{file}.py      # e.g. tests/unit/todos/test_service.py
  api/
    test_{feature}.py     # black box tests per feature, e.g. test_todos.py
```

---

## TDD

TDD is the default workflow on this project, applied with different intensity per layer.

### API tests — TDD is mandatory

The API contract (endpoint, method, request shape, response shape, status codes) is defined before implementation. Write the test against the spec, watch it fail, implement until it passes. This is the natural TDD loop for HTTP APIs and has no legitimate reason to skip.

### Unit tests — TDD where the logic is known upfront

TDD on unit tests is encouraged a much as possible when the logic is known upfront (a pricing rule, a permission check with clear inputs and outputs).


---

## Two test layers, distinct responsibilities

### API tests — black box

The API test treats the entire stack as a black box. Given an HTTP input, assert on all observable outputs:

- HTTP response: status code and response body shape
- DB state: rows created, updated, or deleted as a result of the request
- External side effects: outbound API calls made, events published, emails sent

```python
async def test_create_user(client: AsyncClient, db_session: AsyncSession) -> None:
    response = await client.post("/users/", json={"name": "Jeremy"})

    # HTTP output
    assert response.status_code == 201
    assert response.json()["name"] == "Jeremy"

    # DB output
    user = await db_session.get(User, response.json()["id"])
    assert user is not None
    assert user.name == "Jeremy"
```

API tests require a real database and clean state between tests. They are integration tests by nature — slower to run, but high confidence. Every endpoint must have tests for both happy path and failure cases (see section below).

What API tests do not verify: which internal functions were called, how many queries ran, internal data transformations. Those are implementation details.

### Unit tests — logic only

Unit tests cover functions that contain real logic: branching, calculations, state transitions, complex validation rules. They do not cover a layer by default — they cover logic wherever it lives.

**Test in unit tests:**
- Complex business rules in services (pricing, permissions, discount logic, state machines)
- Edge cases that would require expensive or complex setup to trigger at the API level
- Functions with many input combinations that would cause an explosion of API test scenarios
- Pure transformation and mapping functions

**Do not write unit tests for:**
- Service methods that only delegate to a repository and return the result — there is no logic to test
- Repositories — covered by API tests hitting a real DB
- Simple schemas — Pydantic validates itself
- Route handlers — covered by API tests

The question to ask before writing a unit test: *does this function contain logic I cannot cover through the API test?* If the answer is no, the API test is sufficient. Over-testing thin layers is the most common cause of brittle test suites — a method signature change should not require updating three test files.

---

## Every endpoint: happy path and failure cases

Every route must have at minimum:

- **Happy path**: valid input, expected success response and side effects
- **Validation failure** (`422`): missing required fields, wrong types, constraint violations
- **Not found** (`404`): resource does not exist
- **Business rule violation** (`400`): valid input that fails a domain rule
- **Auth boundaries** (`401` / `403`): unauthenticated and unauthorized access where applicable

```python
# happy path
async def test_create_user(client: AsyncClient, db_session: AsyncSession) -> None:
    response = await client.post("/users/", json={"name": "Jeremy"})
    assert response.status_code == 201
    assert response.json()["name"] == "Jeremy"
    user = await db_session.get(User, response.json()["id"])
    assert user is not None

# validation failure
async def test_create_user_missing_name(client: AsyncClient) -> None:
    response = await client.post("/users/", json={})
    assert response.status_code == 422

# not found
async def test_get_user_not_found(client: AsyncClient) -> None:
    response = await client.get("/users/99999")
    assert response.status_code == 404
```



## 1. One shared client fixture

Use the common `AsyncClient` defined in `conftest.py` and inject it via pytest fixtures. Never instantiate the client inside individual tests.

---

## 2. Override dependencies explicitly — and always clean up

Use FastAPI's `app.dependency_overrides` to swap out real dependencies for fakes in tests that do not need a real DB or external service. Wrap overrides in a fixture to guarantee cleanup even if a test fails.

```python
@pytest.fixture
def override_db(fake_db: FakeDB) -> Generator[None, None, None]:
    app.dependency_overrides[get_db] = lambda: fake_db
    yield
    app.dependency_overrides.clear()
```

Never leave overrides in place across tests — shared state between tests causes hard-to-debug failures.

---

## 3. Never assert only on status code

A 200 with an empty or malformed body is still a broken endpoint.

```python
# weak
assert response.status_code == 200

# correct
assert response.status_code == 200
assert response.json() == {"message": "hello hello!"}
```

---

## 4. pytest-asyncio in auto mode

Set `asyncio_mode = "auto"` in `pyproject.toml` to avoid decorating every async test with `@pytest.mark.asyncio`. Sync test functions are unaffected.

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```