from app.storage.base import StorageBackendInterface
from app.storage.s3_storage import S3Storage
from app.storage.database_storage import DatabaseStorage
from app.storage.local_storage import LocalStorage
from app.storage.ftp_storage import FTPStorage
from app.core.config import StorageBackend, settings

def get_storage_backend(backend_type: StorageBackend = None) -> StorageBackendInterface:
    """Factory function to get the configured storage backend"""
    if backend_type is None:
        backend_type = settings.STORAGE_BACKEND
    
    backends = {
        StorageBackend.S3: S3Storage,
        StorageBackend.DATABASE: DatabaseStorage,
        StorageBackend.LOCAL: LocalStorage,
        StorageBackend.FTP: FTPStorage,
    }
    
    backend_class = backends.get(backend_type)
    if not backend_class:
        raise ValueError(f"Unsupported storage backend: {backend_type}")
    
    return backend_class()