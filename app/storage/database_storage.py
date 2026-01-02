from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend, settings
from app.core.database import async_session
from app.blob_crud import  create_blob_data , create_blob_metadata  , get_blob_data , get_blob_metadata
from app.blob_models  import BlobMetadata
from app.blob_schemas import BlobResponse , BlobCreate
from app.core.logger import   setup_logger

logger =  setup_logger(__name__)

class DatabaseStorage(StorageBackendInterface):
    
    async def save(self, blob_id: str, data: bytes, filename: str, path: str, **kwargs ) -> BlobResponse | None:

        
        logger.debug(f"DatabaseStorage save started for blob_id: {blob_id}")

        # 2️⃣ Build BlobCreate 
        blob = BlobCreate(
            id=blob_id,
            data=data,
        )

        logger.debug(f"Blob Created for blob_id: {blob_id}")

        
        async with async_session() as db:

            # 4️⃣ USE create_blob_data (THIS IS WHAT YOU WANTED)
            blob_data_response = await create_blob_data(db=db, blob=blob)
            logger.debug(f"Blob Created for blob_id: {blob_id}")

            if not blob_data_response:
                logger.warning(f"Error Create Metadata for  blob_id: {blob_id}")
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
            logger.debug(f"Blob metadata created for blob_id: {blob_id}")
            
            if not blob_metadata:
                logger.warning(f"Error create Blob Metadata for blob_id: {blob_id}")
                return None

        # 6️⃣ Return API response
        logger.info(f"Successfully create Blob for blob_id : {blob_id}")
        return BlobResponse(
            id=blob_id,
            data=data,
            size=blob_metadata.size,
            created_at=str(blob_metadata.created_at),
            name=blob_metadata.name,
            path=blob_metadata.path,
            storage_backend=blob_metadata.storage_backend,
            # storage_path=blob_metadata.storage_path,
        )

    
    async def retrieve(self, blob_id: str, **kwargs) -> BlobResponse | None:
        async with async_session() as db:
            
            logger.debug(f"DatabaseStorage.retrieve started blob_id:{blob_id}")

            blob_data = await get_blob_data(db=db, blob_id=blob_id)
            if not blob_data:
                logger.warning(f"Blob data not found blob_id:{blob_id}")
                return None

            blob_metadata = await get_blob_metadata(db=db, blob_id=blob_id)
            if not blob_metadata:
                logger.warning( "Blob metadata not found blob_id {blob_id}")
                return None

            logger.info(f"Blob successfully retrieved from database")
            return BlobResponse(
                id=blob_data.id,
                data=blob_data.data,           # Base64
                size=blob_metadata.size,
                created_at=str(blob_metadata.created_at),
                name=blob_metadata.name,
                path=blob_metadata.path,
                storage_backend=blob_metadata.storage_backend,
                # storage_path=blob_metadata.storage_path,
            )
    
    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.DATABASE