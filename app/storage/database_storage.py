from typing import Optional
import base64
from sqlalchemy import create_engine, Column, String, LargeBinary, MetaData, Table
from sqlalchemy.orm import sessionmaker
from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend, settings
from app.core.database import async_session

class DatabaseStorage(StorageBackendInterface):
    """Database storage backend using a separate table for blob data"""
    
    def __init__(self):
        # Create a separate engine for blob storage if needed
        # Using the same database but different table
        self.db = async_session()
        
        # Define the blob storage table
        self.metadata = MetaData()
        self.blob_table = Table(
            settings.DB_STORAGE_TABLE,
            self.metadata,
            Column('id', String(255), primary_key=True),
            Column('data', LargeBinary, nullable=False),
            extend_existing=True
        )
        
        # Create the table if it doesn't exist
        self.metadata.create_all(bind=self.db.bind)
    
    async def save(self, blob_id: str, data: bytes, **kwargs) -> str:
        """Save data to database table"""
        try:
            # Insert or replace the blob
            stmt = self.blob_table.insert().values(id=blob_id, data=data)
            do_update_stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(data=data)
            )
            self.db.execute(do_update_stmt)
            self.db.commit()
            return blob_id
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to save to database: {str(e)}")
    
    async def retrieve(self, blob_id: str, **kwargs) -> Optional[bytes]:
        """Retrieve data from database table"""
        try:
            result = self.db.execute(
                self.blob_table.select().where(self.blob_table.c.id == blob_id)
            ).fetchone()
            
            if result:
                return result.data
            return None
        except Exception as e:
            raise Exception(f"Failed to retrieve from database: {str(e)}")
    
    async def delete(self, blob_id: str, **kwargs) -> bool:
        """Delete data from database table"""
        try:
            result = self.db.execute(
                self.blob_table.delete().where(self.blob_table.c.id == blob_id)
            )
            self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to delete from database: {str(e)}")
    
    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.DATABASE