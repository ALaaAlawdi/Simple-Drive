from typing import Optional
import base64
from sqlalchemy import  Column, String, LargeBinary, MetaData, Table
from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend, settings
from fastapi import Depends 
from app.core.database import async_session
from app.blob_crud import  create_blob_data , create_blob_metadata  , get_blob_data , get_blob_metadata
from app.blob_models  import BlobMetadata, BlobData  
from app.blob_schemas import BlobResponse , BlobCreate
import uuid

class DatabaseStorage(StorageBackendInterface):
    
    async def save(
        self,
        blob_id: str,
        data: bytes,
        filename: str,
        path: str,
        **kwargs,
    ) -> BlobResponse | None:

        
        # 2️⃣ Build BlobCreate (what create_blob_data expects)
        blob = BlobCreate(
            id=blob_id,
            data=data,
        )

        # 3️⃣ OPEN A REAL SESSION
        async with async_session() as db:

            # 4️⃣ USE create_blob_data (THIS IS WHAT YOU WANTED)
            blob_data_response = await create_blob_data(db=db, blob=blob)
            if not blob_data_response:
                return None

            # 5️⃣ Store metadata in SAME session
            blob_metadata = BlobMetadata(
                id=blob_id,
                size=len(data),
                name=filename,
                path=path,
                storage_backend=settings.STORAGE_BACKEND,
                storage_path=settings.LOCAL_STORAGE_PATH,
            )

            blob_metadata = await create_blob_metadata(db=db, blob_metadata=blob_metadata)
            if not blob_metadata:
                return None

        # 6️⃣ Return API response
        return BlobResponse(
            id=blob_id,
            data=data,
            size=blob_metadata.size,
            created_at=str(blob_metadata.created_at),
            name=blob_metadata.name,
            path=blob_metadata.path,
            storage_backend=blob_metadata.storage_backend,
            storage_path=blob_metadata.storage_path,
        )

    
    async def retrieve(self, blob_id: str, **kwargs) -> BlobResponse | None:
        async with async_session() as db:
            blob_data = await get_blob_data(db=db, blob_id=blob_id)
            if not blob_data:
                return None

            blob_metadata = await get_blob_metadata(db=db, blob_id=blob_id)
            if not blob_metadata:
                return None

            return BlobResponse(
                id=blob_data.id,
                data=blob_data.data,           # Base64
                size=blob_metadata.size,
                created_at=str(blob_metadata.created_at),
                name=blob_metadata.name,
                path=blob_metadata.path,
                storage_backend=blob_metadata.storage_backend,
                storage_path=blob_metadata.storage_path,
            )
    
    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.DATABASE