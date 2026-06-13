from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Dependency overrides
# ---------------------------------------------------------------------------
# Pattern: define one fixture per dependency you need to override.
# Always clear overrides after the test to avoid state leaking between tests.
#
# Example — override the database session:
#
# @pytest.fixture
# def override_db(fake_db: FakeDB) -> Generator[None, None, None]:
#     app.dependency_overrides[get_db] = lambda: fake_db  # noqa: ERA001
#     yield
#     app.dependency_overrides.clear() # noqa: ERA001
#
# Use in a test by adding the fixture as a parameter:
#
# async def test_something(client: AsyncClient, override_db: None) -> None:
#     ...
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Add shared factories, seeders, and other fixtures below as the project grows.
# ---------------------------------------------------------------------------
