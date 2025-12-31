from sqlalchemy import Column, String, DateTime, Integer, Enum, Text, Index
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import StorageBackend
import uuid

class BlobMetadata(Base):
    __tablename__ = "blob_metadata"
    
    id = Column(String(500), primary_key=True, index=True)  # Using Text/Text-like for PostgreSQL
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    storage_backend = Column(Enum(StorageBackend, create_constraint=True), nullable=False)
    storage_path = Column(Text, nullable=True)  # Path/key in the storage backend
    
    # Additional fields
    content_type = Column(String(255), nullable=True)
    checksum = Column(String(64), nullable=True)
    name = Column(String(500), nullable=True)
    path = Column(Text, nullable=True)  # User-provided path
    
    # Composite indexes for better query performance
    __table_args__ = (
        Index('idx_name_path', 'name', 'path'),
        Index('idx_created_at', 'created_at'),
        Index('idx_storage_backend', 'storage_backend'),
    )
    
    def __repr__(self):
        return f"<BlobMetadata(id={self.id}, size={self.size}, backend={self.storage_backend})>"