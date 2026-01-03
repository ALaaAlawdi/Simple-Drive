
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

def test_storage_save_success(client: TestClient, auth_headers, mock_storage):
    files = {'file': ('test.txt', b"content", "text/plain")}
    response = client.post("/api/v1/blobs", headers=auth_headers, files=files)
    
    assert response.status_code == 201
    mock_storage.save.assert_called_once()
    data = response.json()
    assert data["id"] is not None
    # Check if data in response is what we expect (base64 of "content")
    # "content" b64 -> Y29udGVudA==
    # But mock_storage returns valid object. The endpoint returns that object.
    # The endpoint passes "base64_data" to save.
    
    # Let's verify what was passed to save
    args, kwargs = mock_storage.save.call_args
    # blob_id, data, filename, path
    assert kwargs["filename"] == "test.txt"
    # assert kwargs["data"] == b'Y29udGVudA==' # b64 encoded "content"

def test_storage_save_failure(client: TestClient, auth_headers, mock_storage):
    # Simulate DB or Storage error
    mock_storage.save.side_effect = Exception("Storage connection failed")
    
    files = {'file': ('test.txt', b"content", "text/plain")}
    response = client.post("/api/v1/blobs", headers=auth_headers, files=files)
    
    # Endpoint catches Exception and returns 500
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"

def test_storage_retrieve_success(client: TestClient, auth_headers, mock_storage):
    # We need a valid UUID
    import uuid
    blob_id = str(uuid.uuid4())
    
    response = client.get(f"/api/v1/blobs/{blob_id}", headers=auth_headers)
    
    assert response.status_code == 200
    mock_storage.retrieve.assert_called_with(blob_id)

def test_storage_retrieve_not_found(client: TestClient, auth_headers, mock_storage):
    import uuid
    blob_id = str(uuid.uuid4())
    
    # Mock retrieve returning None (not found)
    mock_storage.retrieve.return_value = None
    # We need to clear side_effect if it was set in fixture using a wrapper,
    # but the fixture implements side_effect_retrieve.
    # Let's override side_effect to return None
    mock_storage.retrieve.side_effect = None
    mock_storage.retrieve.return_value = None

    response = client.get(f"/api/v1/blobs/{blob_id}", headers=auth_headers)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Blob not found"
