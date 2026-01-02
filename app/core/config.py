from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os
from enum import Enum

class StorageBackend(str, Enum):
    S3 = "s3"
    DATABASE = "database"
    LOCAL = "local"
    FTP = "ftp"

     
class Settings(BaseSettings):
    # Database settings
    POSTGRESQL_DB_HOST: str = Field(..., env="POSTGRESQL_DB_HOST")
    POSTGRESQL_DB_PORT: int = Field(5432, env="POSTGRESQL_DB_PORT")
    POSTGRESQL_DB_USER: str = Field(..., env="POSTGRESQL_DB_USER")
    POSTGRESQL_DB_PASSWORD: str = Field(..., env="POSTGRESQL_DB_PASSWORD")
    POSTGRESQL_DB_NAME: str = Field(..., env="POSTGRESQL_DB_NAME")

    # authentication
    AUTH_TOKEN: str = "simple-drive-secret-token"

    # Storage configuration
    STORAGE_BACKEND: StorageBackend = StorageBackend.DATABASE
    
    # S3 configuration
    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET: str = "simple-drive"
    S3_REGION: str = "us-east-1"

    # aws credentials
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")    
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field("eu-north-1", env="AWS_REGION")

    # FTP configuration 
    FTP_HOST: str = Field(..., env="FTP_HOST")
    FTP_PORT: int = Field(21, env="FTP_PORT")
    FTP_USERNAME: str = Field(..., env="FTP_USERNAME")
    FTP_PASSWORD: str = Field(..., env="FTP_PASSWORD")  
    FTP_DIRECTORY: str = Field("/", env="FTP_DIRECTORY")

    # Local storage configuration
    LOCAL_STORAGE_PATH: str = "./storage"

    # Database storage configuration
    DB_STORAGE_TABLE: str = "blob_storage"

    # Media directory
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent)
    MEDIA_DIR: str = os.path.join(BASE_DIR, "media")


    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


