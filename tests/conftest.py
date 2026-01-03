import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.security import verify_token

# 🔐 Override auth
async def fake_verify_token():
    return {"sub": "test-user"}

app.dependency_overrides[verify_token] = fake_verify_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
