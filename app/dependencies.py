from typing import Generator
from app.core.database import get_db
from app.core.security import verify_token
from app.storage import get_storage_backend
from app.core.config import settings
from fastapi import Depends
from sqlalchemy.orm import Session

def get_storage():
    """Get the configured storage backend"""
    storage = get_storage_backend(settings.STORAGE_BACKEND)
    yield storage