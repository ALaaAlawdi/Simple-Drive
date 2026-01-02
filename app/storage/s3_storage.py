from datetime import datetime, timezone
from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend
from app.blob_schemas import BlobResponse
from app.s3_client import s3_request


class S3Storage(StorageBackendInterface):

    def _object_key(self, blob_id: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        safe_id = blob_id.replace("/", "_")
        return f"{ts}__{safe_id}.bin"

    def _extract_created_at(self, key: str) -> datetime:
        ts = key.split("/")[-1].split("__", 1)[0]
        return datetime.strptime(ts, "%Y%m%dT%H%M%S%fZ").replace(
            tzinfo=timezone.utc
        )

    async def save(
        self,
        blob_id: str,
        data: bytes,
        filename: str,
        path: str,
        **kwargs,
    ) -> BlobResponse | None:

        object_key = self._object_key(blob_id)
        resp = s3_request("PUT", object_key, data)

        if resp.status_code not in (200, 201):
            return None

        return BlobResponse(
            id=blob_id,
            data=data,
            size=len(data),
            created_at=self._extract_created_at(object_key),
            name=filename,
            path=path,
            storage_backend=StorageBackend.S3,
            storage_path=object_key,
        )

    async def retrieve(self, blob_id:  str, **kwargs) -> BlobResponse | None:

        resp = s3_request("GET", object_key=blob_id)
        
        if resp.status_code != 200:
            return None

        data = resp.content

        return BlobResponse(
            id=blob_id,
            data=data,
            size=len(data),
            created_at=self._extract_created_at(storage_path),
            name="Null",
            path=storage_path,
            storage_backend=StorageBackend.S3,
            storage_path=storage_path,
        )

    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.S3
