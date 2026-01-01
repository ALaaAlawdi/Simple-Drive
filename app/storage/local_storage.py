from pathlib import Path
from datetime import datetime
from app.storage.base import StorageBackendInterface
from app.core.config import settings, StorageBackend
from app.blob_schemas import BlobResponse
from datetime import datetime, timezone
from pathlib import Path

class LocalStorage(StorageBackendInterface):

    def __init__(self):
        self.root = Path(settings.LOCAL_STORAGE_PATH)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, blob_id: str) -> Path:
        created_at = datetime.now(timezone.utc)
        ts = created_at.strftime("%Y%m%dT%H%M%S%fZ")
        safe_id = blob_id.replace("/", "_")

        filename = f"{ts}__{safe_id}.bin"
        return self.root / filename
    
    def _parse_created_at_from_path(self, path: Path) -> datetime:
        # Extract "<timestamp>" from "<timestamp>__<blob_id>.bin"
        ts = path.name.split("__", 1)[0]
        return datetime.strptime(ts, "%Y%m%dT%H%M%S%fZ").replace(tzinfo=timezone.utc)


    async def save(
        self,
        blob_id: str,
        data: bytes,
        filename: str,
        path: str,
        **kwargs,
    ) -> BlobResponse | None:

        file_path = self._path_for(blob_id)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "wb") as f:
                f.write(data)
        except OSError:
            return None

        stat = file_path.stat()

        return BlobResponse(
            id=blob_id,
            data=data,
            size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            name=filename,
            path=path,
            storage_backend=StorageBackend.LOCAL,
            storage_path=str(file_path),
        )

    async def retrieve(self, blob_id: str, **kwargs) -> BlobResponse | None:

        safe_id = blob_id.replace("/", "_")

        matches = list(self.root.glob(f"*__{safe_id}.bin"))
        if not matches:
            return None

        file_path = matches[0]
        
        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except OSError:
            return None

        stat = file_path.stat()

        created_at = self._parse_created_at_from_path(file_path)
        
        return BlobResponse(
            id=blob_id,
            data=data,
            size=stat.st_size,
            created_at=created_at,
            name="Null",          # not persisted
            path=str(file_path),          # not persisted
            storage_backend=StorageBackend.LOCAL,
            storage_path=str(file_path),
        )

    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.LOCAL
