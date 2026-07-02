import aiofiles
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

from config.config import settings


async def save_upload_file(file: UploadFile) -> Path:
    max_size = settings.MAX_FILE_SIZE

    # Tolak lebih awal bila Starlette sudah mengetahui ukuran (hemat I/O disk).
    size = getattr(file, "size", None)
    if size is not None and size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Ukuran file melebihi batas maksimum {max_size} bytes.",
        )

    # Nama file unik + basename saja: cegah tabrakan antar-request bersamaan
    # dan path traversal (mis. filename "../../etc/passwd").
    safe_name = Path(file.filename or "upload").name
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    path = Path(settings.UPLOAD_DIR) / unique_name

    total = 0
    exceeded = False
    async with aiofiles.open(path, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)

            if not chunk:
                break

            total += len(chunk)
            # Defense-in-depth: batasi juga saat streaming (Content-Length bisa
            # bohong / tidak ada). Berhenti sebelum menghabiskan disk & RAM.
            if total > max_size:
                exceeded = True
                break

            await out.write(chunk)

    # Bersihkan file parsial di luar context manager agar file tertutup rapi.
    if exceeded:
        path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Ukuran file melebihi batas maksimum {max_size} bytes.",
        )

    return path
