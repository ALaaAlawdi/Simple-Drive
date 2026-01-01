from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import StorageBackend
from app.blob_schemas import BlobResponse , BlobCreate

class StorageBackendInterface(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def save(self, blob_id: str, data: bytes, filename: str, path: str ,**kwargs) -> BlobCreate:
        """
        Save data to storage backend
        
        Args:
            blob_id: Unique identifier for the blob
            data: Binary data to store
            
        Returns:
            Storage path/key where the data is stored
        """
        pass
    
    @abstractmethod
    async def retrieve(self, blob_id: str, **kwargs) -> BlobResponse:
        """
        Retrieve data from storage backend
        
        Args:
            blob_id: Unique identifier for the blob
            
        Returns:
            Binary data if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_backend_type(self) -> StorageBackend:
        """Return the backend type"""
        pass