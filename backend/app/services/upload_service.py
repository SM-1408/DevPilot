from pathlib import Path
from zipfile import ZipFile
import shutil
import uuid


UPLOAD_DIR = Path("storage/uploads")
EXTRACT_DIR = Path("storage/extracted")


def save_and_extract_zip(file):

    file_id = str(uuid.uuid4())

    upload_path = UPLOAD_DIR / f"{file_id}.zip"
    extract_path = EXTRACT_DIR / file_id

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    with upload_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extract_path.mkdir(parents=True, exist_ok=True)

    with ZipFile(upload_path, "r") as zip_file:
        zip_file.extractall(extract_path)

    return extract_path