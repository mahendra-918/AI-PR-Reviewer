import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.config import settings


@pytest.fixture(autouse=True)
def mock_env_settings(monkeypatch):
    monkeypatch.setattr(settings, "github_webhook_secret", "test_secret_key")
    monkeypatch.setattr(settings, "app_env", "testing")


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
