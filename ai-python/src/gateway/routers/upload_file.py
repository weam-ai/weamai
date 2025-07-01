import aiofiles
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from typing import List
from src.logger.default_logger import logger
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
import pytz
from bson import ObjectId
from src.db.config import db_instance

load_dotenv()

router = APIRouter()

def create_upload_directory():
    """Ensures 'Uploaded_File' folder exists and returns its path."""
    upload_dir = os.path.join(os.getcwd(), "Uploaded_File")
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@router.post("/upload-file")
async def upload(request: Request, files: List[UploadFile] = File(...)):
    uploaded_files = []
    upload_dir = create_upload_directory()
    file_collection = db_instance.get_collection("file")

    for file in files:
        try:
            ext = os.path.splitext(file.filename)[1]
            extension = ext.lstrip(".").lower()
            safe_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(upload_dir, safe_filename)

            # Save the file asynchronously using aiofiles
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await file.read(1024 * 1024):
                    await f.write(chunk)

            # Build URI relative to project root
            relative_uri = os.path.relpath(file_path, os.getcwd()).replace("\\", "/")
            public_uri = f"/{relative_uri}"

            file_size = os.path.getsize(file_path)
            generated_id = ObjectId()
            now = datetime.now(pytz.timezone("Asia/Kolkata"))

            file_metadata = {
                "_id": generated_id,
                "name": file.filename,
                "type": extension,
                "uri": public_uri,
                "mime_type": file.content_type or "application/octet-stream",
                "file_size": str(file_size),
                "module": None,
                "isActive": True,
                "createdAt": now,
                "updatedAt": now,
                "__v": 0
            }

            file_collection.insert_one(file_metadata)

            logger.info(f"Uploaded: {file.filename}")
            uploaded_files.append({
                "original": file.filename,
                "stored": safe_filename,
                "uri": public_uri
            })

        except Exception as e:
            logger.exception(f"Failed to upload {file.filename}")
            raise HTTPException(status_code=500, detail=f"Upload failed for {file.filename}")

        finally:
            await file.close()

    return {
        "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
        "files": uploaded_files
    }

@router.delete("/delete-file/{file_id}")
async def delete_file(file_id: str):
    file_collection = db_instance.get_collection("file")

    try:
        # Validate ObjectId
        if not ObjectId.is_valid(file_id):
            raise HTTPException(status_code=400, detail="Invalid file ID")

        # Fetch the file record from DB
        file_record = file_collection.find_one({"_id": ObjectId(file_id)})

        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")

        # Build absolute file path
        file_path = os.path.join(os.getcwd(), file_record['uri'].lstrip("/"))

        # Delete file from filesystem
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            logger.warning(f"File not found on disk: {file_path}")

        # Delete from MongoDB
        file_collection.delete_one({"_id": ObjectId(file_id)})

        logger.info(f"Deleted file {file_record['name']} (ID: {file_id})")
        return {"message": "File deleted successfully", "file_id": file_id}

    except Exception as e:
        logger.exception(f"Error deleting file {file_id}")
        raise HTTPException(status_code=500, detail="Failed to delete file")