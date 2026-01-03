
import pytest
from app.blob_schemas import BlobCreate, BlobResponse
from datetime import datetime, timezone
import base64
import uuid

def test_blob_create_valid_base64():
    data = base64.b64encode(b"test string")
    blob = BlobCreate(data=data)
    assert blob.data == data

def test_blob_create_invalid_base64():
    # "Invalid" in terms of base64 content. 
    # Invalid characters or padding.
    data = b"!!!invalid_base64!!!" 
    with pytest.raises(ValueError) as excinfo:
        BlobCreate(data=data)
    # Pydantic 2.x error structure might differ, checking "Invalid base64 data" logic
    assert "Invalid base64 data" in str(excinfo.value)

def test_blob_response_valid_base64():
    data = base64.b64encode(b"test string")
    blob_id = uuid.uuid4()
    blob = BlobResponse(
        id=blob_id,
        data=data,
        size=10,
        created_at=datetime.now(timezone.utc),
        name="test.txt",
        path="path/to/test.txt"
    )
    assert blob.data == data

def test_blob_response_path_validation():
    data = base64.b64encode(b"test")
    blob_id = uuid.uuid4()
    # Test path cleanup and validation
    # This assumes validate_path is working
    blob = BlobResponse(
        id=blob_id,
        data=data,
        size=4,
        created_at=datetime.now(timezone.utc),
        path="/folder/file.txt" 
    )
    assert blob.path == "folder/file.txt"

    with pytest.raises(ValueError):
        BlobResponse(
            id=blob_id,
            data=data,
            size=4,
            created_at=datetime.now(timezone.utc),
            path="../sensitive/file.txt"
        )
