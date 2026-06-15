from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
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
# Settings override
# ---------------------------------------------------------------------------
# Swaps get_settings in dependency_overrides, so it only reaches routes that read
# settings at REQUEST time via SettingsDep. It cannot change values consumed at app
# construction (docs_url, redoc_url, openapi_url) — those are fixed on the FastAPI
# instance at import and need a freshly built app to vary.
# ---------------------------------------------------------------------------


@pytest.fixture
def override_settings(request: pytest.FixtureRequest) -> Generator[Settings]:
    """Inject custom Settings into routes that depend on SettingsDep.

    Two ways to use it:
        1. Defaults: request the fixture as-is and a default Settings() is injected.
               def test_x(client, override_settings): ...
        2. Custom values: parametrize indirectly with the values to override.
               @pytest.mark.parametrize("override_settings", [{"environment": "production"}], indirect=True)
               def test_x(client, override_settings): ...
    """
    test_settings = Settings.model_validate(getattr(request, "param", {}))
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield test_settings
    del app.dependency_overrides[get_settings]


# ---------------------------------------------------------------------------
# Add shared factories, seeders, and other fixtures below as the project grows.
# ---------------------------------------------------------------------------
