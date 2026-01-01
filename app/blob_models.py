from sqlalchemy import UUID, Column, String, DateTime, Integer, Enum, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import StorageBackend
from sqlalchemy.orm import relationship
import uuid


class BlobData(Base):
    __tablename__ = "blob_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    data = Column(BYTEA, nullable=False)  
    
    # Relationship with BlobMetadata
    blob_metadata = relationship("BlobMetadata", back_populates="blob_data", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BlobData(id={self.id})>"
    

class BlobMetadata(Base):
    __tablename__ = "blob_metadata"
    
    id = Column(UUID(as_uuid=True), ForeignKey("blob_data.id", ondelete="CASCADE"), primary_key=True, default=uuid.uuid4)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    storage_backend = Column(Enum(StorageBackend, create_constraint=True), nullable=False)
    storage_path = Column(Text, nullable=True) 
    
    name = Column(String(500), nullable=True)
    path = Column(Text, nullable=True)  
    
    # Relationship with BlobData
    blob_data = relationship("BlobData", back_populates="blob_metadata")

    # Composite indexes for better query performance
    __table_args__ = (
        Index('idx_name_path', 'name', 'path'),
        Index('idx_created_at', 'created_at'),
        Index('idx_storage_backend', 'storage_backend'),
    )
    
    def __repr__(self):
        return f"<BlobMetadata(id={self.id}, size={self.size}, backend={self.storage_backend})>"