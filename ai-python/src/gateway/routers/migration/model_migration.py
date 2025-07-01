from fastapi import HTTPException, status, Depends, APIRouter
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.gateway.jwt_decode import get_user_data
from datetime import datetime
import pytz
from pydantic import BaseModel

router = APIRouter()

class ModelOpenRouterMigration(BaseModel):
    title: str
    code: str
    provider: str
    isActive: bool = True
    seq: int = 2

@router.post(
    "/migrate-openrouter-model",
    summary="Migrate a model into the 'model' collection",
    description="Migrate a new record into the model collection dynamically.",
    response_description="Migration status message",
)
async def migrate_openrouter_model(request: ModelOpenRouterMigration, current_user=Depends(get_user_data)):
    """
    Dynamically migrate a model into the model collection.

    **Request Body:**
    - `title` (str): The title of the model.
    - `code` (str): A unique code identifier for the model.
    - `provider` (str): A unique provider for the model.
    - `isActive` (bool, optional): The active status of the model. Defaults to `True`.
    - `seq` (int): The sequence number for ordering.
    """
    try:
        model_collection = db_instance.get_collection("model")
        
        # Check if the model record exists based on the provided code
        existing_record = model_collection.find_one({"code": request.code})
        
        if not existing_record:
            timezone = pytz.timezone("Asia/Kolkata")
            current_datetime = datetime.now(timezone)

            new_record = {
                "title": request.title,
                "code": request.code,
                "provider": request.provider,
                "isActive": request.isActive,
                "createdAt": current_datetime,
                "updatedAt": current_datetime,
                "__v": 0,
                "seq": request.seq
            }
            model_collection.insert_one(new_record)
            logger.info(f"Created a new '{request.code}' record in the model collection.")
            return {"message": f"Model '{request.title}' migrated successfully."}
        
        return {"message": f"Model with code '{request.code}' already exists."}
    
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error during the migration process.")

class ModelMigration(BaseModel):
    title: str
    code: str
    isActive: bool = True
    seq: int = 2

@router.post(
    "/migrate-model",
    summary="Migrate a model into the 'model' collection",
    description="Migrate a new record into the model collection dynamically.",
    response_description="Migration status message",
)
async def migrate_model(request: ModelMigration, current_user=Depends(get_user_data)):
    """
    Dynamically migrate a model into the model collection.

    **Request Body:**
    - `title` (str): The title of the model.
    - `code` (str): A unique code identifier for the model.
    - `isActive` (bool, optional): The active status of the model. Defaults to `True`.
    - `seq` (int): The sequence number for ordering.
    """
    try:
        model_collection = db_instance.get_collection("model")
        
        # Check if the model record exists based on the provided code
        existing_record = model_collection.find_one({"code": request.code})
        
        if not existing_record:
            timezone = pytz.timezone("Asia/Kolkata")
            current_datetime = datetime.now(timezone)

            new_record = {
                "title": request.title,
                "code": request.code,
                "isActive": request.isActive,
                "createdAt": current_datetime,
                "updatedAt": current_datetime,
                "__v": 0,
                "seq": request.seq
            }
            model_collection.insert_one(new_record)
            logger.info(f"Created a new '{request.code}' record in the model collection.")
            return {"message": f"Model '{request.title}' migrated successfully."}
        
        return {"message": f"Model with code '{request.code}' already exists."}
    
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error during the migration process.")