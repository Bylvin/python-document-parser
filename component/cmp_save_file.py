import aiofiles
import uuid
from pathlib import Path

from fastapi import UploadFile

from config.config import settings


async def save_upload_file(file: UploadFile) -> Path:
    filename = file.filename
    path = Path(settings.UPLOAD_DIR) / filename
    async with aiofiles.open(path, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)

            if not chunk:
                break
            await out.write(chunk)
    return path
