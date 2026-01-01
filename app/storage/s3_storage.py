import hashlib
import hmac
import datetime
from typing import Optional
import httpx
from urllib.parse import urlparse, quote
from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend, settings
import base64

class S3Storage(StorageBackendInterface):
    """S3-compatible storage backend using raw HTTP requests"""
    
    def __init__(self):
        self.endpoint = settings.S3_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.bucket = settings.S3_BUCKET
        self.region = settings.S3_REGION

        # Initialize HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _sign_request(self, method: str, path: str, headers: dict, payload: bytes = b"") -> dict:
        """Generate AWS Signature Version 4 for the request"""
        # This is a simplified version - production should implement full SigV4
        # For simplicity with MinIO and similar, we might use pre-signed URLs or simpler auth
        # Here's a basic implementation for demonstration
        
        # For actual S3-compatible services, you'd need full SigV4 implementation
        # This is a placeholder that would need to be completed
        
        # For now, we'll use a simpler approach if endpoint allows
        if self.access_key and self.secret_key:
            headers['Authorization'] = f"AWS {self.access_key}:{self._get_signature(method, path)}"
        
        return headers
    
    def _get_signature(self, method: str, path: str) -> str:
        """Generate a simple signature (not full SigV4)"""
        # Simplified for demonstration - real implementation needs full SigV4
        string_to_sign = f"{method}\n\n\n\n{path}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        return base64.b64encode(signature).decode()
    
    async def save(self, blob_id: str, data: bytes, filename: str, path: str, **kwargs) -> str:
        """Save data to S3-compatible storage"""
        path = f"/{self.bucket}/{blob_id}"
        url = f"{self.endpoint}{path}"
        
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(data)),
        }
        
        # Sign the request
        headers = self._sign_request('PUT', path, headers, data)
        
        try:
            response = await self.client.put(url, content=data, headers=headers)
            response.raise_for_status()
            return blob_id
        except Exception as e:
            raise Exception(f"Failed to save to S3: {str(e)}")
    
    async def retrieve(self, blob_id: str, **kwargs) -> Optional[bytes]:
        """Retrieve data from S3-compatible storage"""
        path = f"/{self.bucket}/{blob_id}"
        url = f"{self.endpoint}{path}"
        
        headers = {}
        headers = self._sign_request('GET', path, headers)
        
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise Exception(f"Failed to retrieve from S3: {str(e)}")
    
   
    
    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.S3
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def __aenter__(self):
        return self