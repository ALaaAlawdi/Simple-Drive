import os
import hashlib
from pathlib import Path
from typing import Optional
from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend, settings

class LocalStorage(StorageBackendInterface):
    """Local filesystem storage backend"""
    
    def __init__(self):
        self.storage_path = Path(settings.local_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, blob_id: str) -> Path:
        """Generate file path from blob ID"""
        # Create a subdirectory structure based on hash for better distribution
        hash_obj = hashlib.md5(blob_id.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Create directory structure: first 2 chars / next 2 chars
        dir_path = self.storage_path / hash_hex[:2] / hash_hex[2:4]
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return dir_path / blob_id
    
    async def save(self, blob_id: str, data: bytes, **kwargs) -> str:
        """Save data to local filesystem"""
        file_path = self._get_file_path(blob_id)
        
        try:
            with open(file_path, 'wb') as f:
                f.write(data)
            return str(file_path.relative_to(self.storage_path))
        except Exception as e:
            raise Exception(f"Failed to save to local storage: {str(e)}")
    
    async def retrieve(self, blob_id: str, **kwargs) -> Optional[bytes]:
        """Retrieve data from local filesystem"""
        file_path = self._get_file_path(blob_id)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to retrieve from local storage: {str(e)}")
    
    async def delete(self, blob_id: str, **kwargs) -> bool:
        """Delete data from local filesystem"""
        file_path = self._get_file_path(blob_id)
        
        if file_path.exists():
            try:
                file_path.unlink()
                
                # Try to remove empty parent directories
                parent = file_path.parent
                while parent != self.storage_path and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                
                return True
            except Exception:
                return False
        return False
    
    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.LOCAL