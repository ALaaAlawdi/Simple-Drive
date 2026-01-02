from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.core.database import AsyncSession
from app.core.database import get_db
from app.core.security import verify_token
from app.blob_schemas import BlobCreate, BlobResponse
from app.core.logger import setup_logger
from app.core.config import settings
import base64
import uuid
from app.storage import get_storage_backend

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/blobs", response_model=BlobResponse, status_code=201)
async def create_blob(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    try:
        # 1️⃣ Read bytes
        file_bytes: bytes = await file.read()
        # 2️⃣ Extract filename
        filename = file.filename
        # 3️⃣ Optional path logic
        path = f"{settings.MEDIA_DIR}/{filename}"
        # 2️⃣ Encode → Base64
        base64_data = base64.b64encode(file_bytes)#

        logger.debug(f"Base64 encoded data size: {len(base64_data)}")

        storage_backend = get_storage_backend()

        blob_id = str(uuid.uuid4())
        logger.debug(f"Generated blob ID: {blob_id}")

        blob_data_response = await storage_backend.save(    
            blob_id=blob_id,
            data=base64_data,
            filename=filename,
            path=path,
        )

        logger.debug(f"Blob data response: {blob_data_response}")

        if not blob_data_response:
            logger.error("Failed to save blob data")
            raise HTTPException(status_code=500, detail="Failed to save blob data")
        
        logger.info(f"Blob created with ID: {blob_data_response.id}")
        return blob_data_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating blob: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/blobs/{blob_id}", response_model=BlobResponse)
async def get_blob(
    blob_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_token),
):
    try:
        storage_backend = get_storage_backend()
        blob_metadata = await storage_backend.retrieve(str(blob_id))

        if not blob_metadata:
            raise HTTPException(status_code=404, detail="Blob not found")

        return BlobResponse(
            id=blob_id,
            data=blob_metadata.data,
            size=blob_metadata.size,
            created_at=blob_metadata.created_at,
            name=blob_metadata.name,
            path=blob_metadata.path,
            storage_backend=blob_metadata.storage_backend,
            storage_path=blob_metadata.storage_path,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving blob {blob_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
