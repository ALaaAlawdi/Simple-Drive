from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import base64

class BlobCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=255)
    data: str  # Base64 encoded
    name: Optional[str] = None
    path: Optional[str] = None
    
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
            if '..' in v or v.startswith('/'):
                raise ValueError("Invalid path format")
            # Clean up path
            v = v.strip('/')
        return v

class BlobResponse(BaseModel):
    id: str
    data: str
    size: int
    created_at: datetime
    name: Optional[str] = None
    path: Optional[str] = None
    
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    detail: str

class StorageConfig(BaseModel):
    backend: str
    config: dict