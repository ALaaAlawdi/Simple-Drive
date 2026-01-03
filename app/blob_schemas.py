from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import base64
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, field_serializer



class BlobCreate(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)  
    data: bytes  # Base64 encoded

    @field_validator('data')
    def validate_base64(cls, v):
        try:
            # Try to decode the base64 data
            base64.b64decode(v, validate=True)
            return v
        except Exception:
            raise ValueError("Invalid base64 data")

    model_config = {"from_attributes": True}
  

class BlobResponse(BaseModel):
    id: uuid.UUID
    data: bytes
    size: int
    created_at: datetime
    name: Optional[str] = None
    path: Optional[str] = None
    storage_backend: Optional[str] = None
    storage_path: Optional[str] = None

    @field_validator('data')
    def validate_base64(cls, v):
        try:
            # Try to decode the base64 data
            base64.b64decode(v, validate=True)
            return v
        except Exception:
            raise ValueError("Invalid base64 data")

    @field_validator('path')
    def validate_path(cls, v):
        if v is not None:
            if '..' in v:
                raise ValueError("Invalid path format")
            # Clean up path
            v = v.strip('/')
            # Also handle backslashes for Windows consistency if needed, but let's stick to simple fix first.
            v = v.replace('\\', '/') # Normalize to forward slashes for consistency
        return v

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        return (
            dt.astimezone(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    detail: str

class StorageConfig(BaseModel):
    backend: str
    config: dict