from app.core.database import AsyncSession
from sqlalchemy.future import select
from app.blob_models import BlobData, BlobMetadata
from app.blob_schemas import BlobCreate, BlobResponse
from app.core.logger import setup_logger
import base64

logger = setup_logger(__name__)

# ---------- BlobData ----------
async def create_blob_data(
    blob: BlobCreate,
    db: AsyncSession ,
) -> BlobResponse | None:
    try:
        #  require: decode Base64 → bytes
        binary_data = base64.b64decode(blob.data, validate=True)

        db_blob = BlobData(
            id=blob.id,
            data=binary_data,   # BYTEA 
        )

        db.add(db_blob)
        await db.commit()
        await db.refresh(db_blob)

        return BlobCreate(
            id=db_blob.id,
            data=blob.data,            # return Base6
        )

    except Exception as e:
        logger.error(f"Error creating BlobData with ID {blob.id}: {e}")
        return None

# ---------- Retrieve BlobData ----------
async def get_blob_data(
    blob_id,
    db: AsyncSession,
) -> BlobCreate | None:
    try:
        result = await db.execute(
            select(BlobData).where(BlobData.id == blob_id)
        )
        db_blob = result.scalar_one_or_none()

        if not db_blob:
            return None

        # bytes → Base64
        base64_data = base64.b64encode(db_blob.data).decode("utf-8")

        return BlobCreate(
            id=blob_id,
            data=base64_data
        )

    except Exception as e:
        logger.error(f"Error retrieving BlobData with ID {blob_id}: {e}")
        return None


# ---------- BlobMetadata ----------
async def create_blob_metadata(
    db: AsyncSession,
    blob_metadata: BlobMetadata,
) -> BlobMetadata | None:
    try:
        db.add(blob_metadata)
        await db.commit()
        await db.refresh(blob_metadata)
        return blob_metadata
    except Exception as e:
        logger.error(f"Error creating BlobMetadata with ID {blob_metadata.id}: {e}")
        return None

# ---------- Retrieve BlobMetadata ----------
async def get_blob_metadata(
    db: AsyncSession,
    blob_id: str,
) -> BlobResponse | None:
    try:
        result = await db.execute(
            select(BlobMetadata).where(BlobMetadata.id == blob_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error retrieving BlobMetadata with ID {blob_id}: {e}")
        return None
