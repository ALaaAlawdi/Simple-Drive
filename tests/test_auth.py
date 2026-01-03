from fastapi.testclient import TestClient
from app.main import app

def test_missing_auth_token():
    

    client = TestClient(app)

    response = client.post(
        "/api/v1/blobs",
        files={"file": ("test.txt", b"hello")},
        headers={},  # explicitly no Authorization
    )

    assert response.status_code in (401, 403)

