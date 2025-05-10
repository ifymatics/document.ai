import magic
from typing import Tuple
from fastapi import HTTPException
from app.schemas.document import FileType

ALLOWED_MIME_TYPES = {
    'application/pdf': FileType.PDF,
    'image/jpeg': FileType.JPEG,
    'image/png': FileType.PNG,
    'image/jpg': FileType.JPEG
}


def validate_file_type(file_bytes: bytes) -> Tuple[FileType, str]:
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_bytes)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {mime_type}"
        )

    return ALLOWED_MIME_TYPES[mime_type], mime_type


def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1].lower()