from pathlib import Path
from fastapi import UploadFile
import shutil
import uuid

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_file_extension(extension: str, allowed_extensions: set[str]) -> bool:
    return extension.lower() in allowed_extensions


def save_upload_file(file: UploadFile) -> Path:
    extension = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / unique_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path