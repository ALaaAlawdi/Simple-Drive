from ftplib import FTP
from io import BytesIO
from datetime import datetime, timezone

from app.storage.base import StorageBackendInterface
from app.core.config import StorageBackend
from app.blob_schemas import BlobResponse
from app.core.config import settings


class FTPStorage(StorageBackendInterface):

    def __init__(self):
        self.host = settings.FTP_HOST
        self.port = settings.FTP_PORT
        self.username = settings.FTP_USERNAME
        self.password = settings.FTP_PASSWORD
        self.directory = settings.FTP_DIRECTORY

    # ---------- internal helpers ----------

    def _connect(self) -> FTP:
        ftp = FTP()
        ftp.connect(self.host, self.port)
        ftp.login(self.username, self.password)

        if self.directory:
            ftp.cwd(self.directory)

        return ftp

    def _object_key(self, blob_id: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        safe_id = blob_id.replace("/", "_")
        return f"{ts}__{safe_id}.bin"

    def _extract_created_at(self, key: str) -> datetime:
        ts = key.split("__", 1)[0]
        return datetime.strptime(ts, "%Y%m%dT%H%M%S%fZ").replace(
            tzinfo=timezone.utc
        )

    def _find_key(self, ftp: FTP, blob_id: str) -> str | None:
        safe_id = blob_id.replace("/", "_")
        suffix = f"__{safe_id}.bin"

        for name in ftp.nlst():
            if name.endswith(suffix):
                return name

        return None

    # ---------- interface methods ----------

    async def save(
        self,
        blob_id: str,
        data: bytes,
        filename: str,
        path: str,
        **kwargs,
    ) -> BlobResponse | None:

        ftp = self._connect()
        object_key = self._object_key(blob_id)

        with BytesIO(data) as buffer:
            ftp.storbinary(f"STOR {object_key}", buffer)

        ftp.quit()

        return BlobResponse(
            id=blob_id,
            data=data,
            size=len(data),
            created_at=self._extract_created_at(object_key),
            name=filename,
            path=path,
            storage_backend=StorageBackend.FTP,
            storage_path=object_key,
        )

    async def retrieve(self, blob_id: str, **kwargs) -> BlobResponse | None:
        ftp = self._connect()

        storage_path = self._find_key(ftp, blob_id)
        if not storage_path:
            ftp.quit()
            return None

        buffer = BytesIO()
        ftp.retrbinary(f"RETR {storage_path}", buffer.write)
        ftp.quit()

        data = buffer.getvalue()

        return BlobResponse(
            id=blob_id,
            data=data,
            size=len(data),
            created_at=self._extract_created_at(storage_path),
            name="unknown",
            path=storage_path,
            storage_backend=StorageBackend.FTP,
            storage_path=storage_path,
        )

    def get_backend_type(self) -> StorageBackend:
        return StorageBackend.FTP
