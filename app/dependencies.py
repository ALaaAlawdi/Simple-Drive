from app.core.config import settings, StorageBackend
from app.storage.s3_storage import S3Storage
from app.storage.database_storage import DatabaseStorage
from app.storage.local_storage import LocalStorage
from app.storage.ftp_storage import FTPStorage

def get_storage_backend():
    backend = settings.STORAGE_BACKEND
    if backend == StorageBackend.S3:
        return S3Storage()
    elif backend == StorageBackend.DATABASE:
        return DatabaseStorage()
    elif backend == StorageBackend.LOCAL:
        return LocalStorage()
    elif backend == StorageBackend.FTP:
        return FTPStorage()
    else:
        raise ValueError(f"Unsupported storage backend: {backend}")