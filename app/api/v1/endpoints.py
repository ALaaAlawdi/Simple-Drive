import base64
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.schemas import schemas
from app.core.database import get_db
from app.core.security import verify_token
from app.dependencies import get_storage
from app.models import models
from app.storage.base import StorageBackendInterface


router = APIRouter()

@router.post("/blobs", response_model=schemas.BlobResponse, status_code=201)
async def create_blob(
    blob: schemas.BlobCreate,
    db: Session = Depends(get_db),
    storage: StorageBackendInterface = Depends(get_storage),
    auth: dict = Depends(verify_token)
):
    """
    Create a new blob
    
    - **id**: Unique identifier for the blob
    - **data**: Base64-encoded binary data
    - **name**: Optional name for the blob
    - **path**: Optional path for the blob
    """
    # Decode base64 data
    try:
        binary_data = base64.b64decode(blob.data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 data")
    
    # Check if blob already exists
    existing = db.query(models.BlobMetadata).filter(models.BlobMetadata.id == blob.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Blob with this ID already exists")
    
    # Save to storage backend
    try:
        storage_path = await storage.save(blob.id, binary_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save blob: {str(e)}")
    
    # Create metadata record
    db_blob = models.BlobMetadata(
        id=blob.id,
        size=len(binary_data),
        storage_backend=storage.get_backend_type(),
        storage_path=storage_path,
        name=blob.name,
        path=blob.path
    )
    
    db.add(db_blob)
    db.commit()
    db.refresh(db_blob)
    
    # Return response
    return {
        "id": db_blob.id,
        "data": blob.data,  # Return the original base64 data
        "size": db_blob.size,
        "created_at": db_blob.created_at,
        "name": db_blob.name,
        "path": db_blob.path
    }

@router.get("/blobs/{blob_id}", response_model=schemas.BlobResponse)
async def get_blob(
    blob_id: str,
    db: Session = Depends(get_db),
    storage: StorageBackendInterface = Depends(get_storage),
    auth: dict = Depends(verify_token)
):
    """
    Retrieve a blob by ID
    
    - **blob_id**: Unique identifier of the blob to retrieve
    """
    # Get metadata
    db_blob = db.query(models.BlobMetadata).filter(models.BlobMetadata.id == blob_id).first()
    if not db_blob:
        raise HTTPException(status_code=404, detail="Blob not found")
    
    # Retrieve data from storage backend
    try:
        binary_data = await storage.retrieve(blob_id)
        if binary_data is None:
            raise HTTPException(status_code=404, detail="Blob data not found in storage")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve blob: {str(e)}")
    
    # Encode data to base64
    base64_data = base64.b64encode(binary_data).decode('utf-8')
    
    return {
        "id": db_blob.id,
        "data": base64_data,
        "size": db_blob.size,
        "created_at": db_blob.created_at,
        "name": db_blob.name,
        "path": db_blob.path
    }

@router.get("/blobs", response_model=List[schemas.BlobResponse])
async def list_blobs(
    name: Optional[str] = Query(None, description="Filter by name"),
    path: Optional[str] = Query(None, description="Filter by path"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_token)
):
    """
    List blobs with optional filtering by name or path
    
    - **name**: Filter blobs by name
    - **path**: Filter blobs by path
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    query = db.query(models.BlobMetadata)
    
    if name:
        query = query.filter(models.BlobMetadata.name == name)
    if path:
        query = query.filter(models.BlobMetadata.path == path)
    
    blobs = query.offset(skip).limit(limit).all()
    
    # Note: This endpoint doesn't return the actual data, just metadata
    # To get data, use the GET /blobs/{id} endpoint
    return [
        {
            "id": blob.id,
            "data": "",  # Empty data for list endpoint
            "size": blob.size,
            "created_at": blob.created_at,
            "name": blob.name,
            "path": blob.path
        }
        for blob in blobs
    ]

@router.delete("/blobs/{blob_id}", status_code=204)
async def delete_blob(
    blob_id: str,
    db: Session = Depends(get_db),
    storage: StorageBackendInterface = Depends(get_storage),
    auth: dict = Depends(verify_token)
):
    """
    Delete a blob by ID
    
    - **blob_id**: Unique identifier of the blob to delete
    """
    # Get metadata
    db_blob = db.query(models.BlobMetadata).filter(models.BlobMetadata.id == blob_id).first()
    if not db_blob:
        raise HTTPException(status_code=404, detail="Blob not found")
    
    # Delete from storage backend
    try:
        deleted = await storage.delete(blob_id)
        if not deleted:
            # Data not found in storage, but we'll still delete metadata
            pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete blob from storage: {str(e)}")
    
    # Delete metadata
    db.delete(db_blob)
    db.commit()
    
    return None  # 204 No Content