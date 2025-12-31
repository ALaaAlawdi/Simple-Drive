from ftplib import FTP
import io
from typing import Optional
from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend, settings

class FTPStorage(StorageBackendInterface):
    """FTP storage backend (Bonus)"""
    
    def __init__(self):
        self.host = settings.FTP_HOST
        self.port = settings.FTP_PORT
        self.username = settings.FTP_USERNAME
        self.password = settings.FTP_PASSWORD
        self.directory = settings.FTP_DIRECTORY
        
        # Connect to FTP server
        self.ftp = FTP()
        self._connect()
    
    def _connect(self):
        """Establish FTP connection"""
        try:
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.username, self.password)
            
            # Change to working directory
            self.ftp.cwd(self.directory)
        except Exception as e:
            raise Exception(f"Failed to connect to FTP server: {str(e)}")
    
    async def save(self, blob_id: str, data: bytes, **kwargs) -> str:
        """Save data to FTP server"""
        try:
            # Create a bytes buffer
            buffer = io.BytesIO(data)
            
            # Store the file
            self.ftp.storbinary(f'STOR {blob_id}', buffer)
            return blob_id
        except Exception as e:
            raise Exception(f"Failed to save to FTP: {str(e)}")
        finally:
            buffer.close()
    
    async def retrieve(self, blob_id: str, **kwargs) -> Optional[bytes]:
        """Retrieve data from FTP server"""
        try:
            # Create a bytes buffer
            buffer = io.BytesIO()
            
            # Retrieve the file
            self.ftp.retrbinary(f'RETR {blob_id}', buffer.write)
            
            # Get the data
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            # Check if file doesn't exist
            if "550" in str(e):  # File not found error
                return None
            raise Exception(f"Failed to retrieve from FTP: {str(e)}")
        finally:
            buffer.close()
    
    async def delete(self, blob_id: str, **kwargs) -> bool:
        """Delete data from FTP server"""
        try:
            self.ftp.delete(blob_id)
            return True
        except Exception as e:
            # Check if file doesn't exist
            if "550" in str(e):  # File not found error
                return False
            raise Exception(f"Failed to delete from FTP: {str(e)}")
    
    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.FTP
    
    def __del__(self):
        """Close FTP connection on destruction"""
        if hasattr(self, 'ftp'):
            try:
                self.ftp.quit()
            except:
                self.ftp.close()