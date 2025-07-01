from fastapi import HTTPException, status, Depends, APIRouter
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.gateway.jwt_decode import get_user_data
from datetime import datetime
import pytz
from pydantic import BaseModel

router = APIRouter()

class ApiKeyMigrationRequest(BaseModel):
    name: str
    code: str
    details: dict = {}


@router.post(
    "/migrate-setting",
    summary="Insert or Update record in 'setting' collection",
    description="Upserts a record in the 'setting' collection.",
    response_description="Migration status message",
)
async def migrate_setting(request: ApiKeyMigrationRequest, current_user=Depends(get_user_data)):
    """Insert or update a record in the setting collection."""
    try:
        # Fetch the setting collection
        setting_collection = db_instance.get_collection("setting")

        # Fetch existing record
        existing_record = setting_collection.find_one({"name": request.name})
        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        # If record exists, update it
        if existing_record:
            update_result = setting_collection.update_one(
                {"name": request.name},
                {"$set": {
                    "code": request.code,
                    "details": request.details,
                    "updatedAt": current_datetime
                }},
            )
            if update_result.modified_count > 0:
                return {"message": "Record updated successfully"}
            else:
                return {"message": "No changes made"}
        else:
            # Insert new record
            new_record = {
                "name": request.name,
                "code": request.code,
                "details": request.details,
                "createdAt": current_datetime,
                "updatedAt": current_datetime,
                "__v": 0
            }
            setting_collection.insert_one(new_record)
            return {"message": "New record inserted successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")