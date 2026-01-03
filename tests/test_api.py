
import pytest
from fastapi.testclient import TestClient
import uuid

def test_get_blob_contract(client: TestClient, auth_headers, mock_storage):
    blob_id = str(uuid.uuid4())
    
    # Ensure mock returns expected fields for the response model
    # The fixture already returns a class with data, size, created_at, name, path
    # We should verify the JSON response has these keys
    
    response = client.get(f"/api/v1/blobs/{blob_id}", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.json()
    
    expected_keys = {"id", "data", "size", "created_at", "name", "path", "storage_backend", "storage_path"}
    assert expected_keys.issubset(json_data.keys())
    
    assert json_data["id"] == blob_id
    # data from fixture is b"testdata" => b64 encoded in JSON typically?
    # Pydantic Bytes field checks: response model result usage.
    # If the response model has `data: bytes`, FastAPI/Pydantic serializes it to Base64 string automatically in JSON.
    assert isinstance(json_data["data"], str) 

def test_create_blob_contract(client: TestClient, auth_headers, mock_storage):
    files = {'file': ('contract_test.txt', b"contract data", "text/plain")}
    response = client.post("/api/v1/blobs", headers=auth_headers, files=files)
    
    assert response.status_code == 201
    json_data = response.json()
    
    # Response model is BlobCreate: id, data
    assert "id" in json_data
    assert "data" in json_data
    # It shouldn't necessarily have full metadata if response_model=BlobCreate
    # Let's check endpoints.py: @router.post(..., response_model=BlobCreate)
    # So it should ONLY return id and data.
    
    assert "name" not in json_data
    assert "size" not in json_data
