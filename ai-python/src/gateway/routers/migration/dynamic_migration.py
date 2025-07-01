from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, model_validator
from typing import Literal, Dict, Any, List, Optional, Union
from datetime import datetime
import pytz
from bson import ObjectId

from src.db.config import db_instance
from src.gateway.jwt_decode import get_user_data

router = APIRouter()

# Allowed Mongo operations
ALLOWED_ACTIONS = {"create", "update", "delete"}


def convert_object_ids(obj: Any) -> Any:
    """
    Recursively convert valid ObjectId strings to ObjectId instances.
    """
    if isinstance(obj, dict):
        return {k: convert_object_ids(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_object_ids(i) for i in obj]
    if isinstance(obj, str) and ObjectId.is_valid(obj):
        return ObjectId(obj)
    return obj

class MongoOperationRequest(BaseModel):
    action: Literal["create", "update", "delete"]
    collection_name: str
    data: Optional[List[Dict[str, Any]]] = None
    filter_condition: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_required_fields(self) -> "MongoOperationRequest":
        """
        Ensure required fields are present based on the action type.
        """
        if self.action == "create" and not self.data:
            raise ValueError("Field 'data' is required for create action.")
        if self.action == "update":
            if not self.data:
                raise ValueError("Field 'data' is required for update action.")
            if not self.filter_condition:
                raise ValueError("Field 'filter_condition' is required for update action.")
        if self.action == "delete" and not self.filter_condition:
            raise ValueError("Field 'filter_condition' is required for delete action.")
        return self


@router.post("/mongo-operation")
async def dynamic_mongo_operations(request: MongoOperationRequest,current_user: dict = Depends(get_user_data)):
    """
    Handle create, update, or delete operations on MongoDB collections.
    """
    if request.action not in ALLOWED_ACTIONS:
        raise HTTPException(status_code=400, detail="Invalid action type.")

    try:
        collection = db_instance.get_collection(request.collection_name)
        current_datetime = datetime.now(pytz.timezone("Asia/Kolkata"))

        if request.action == "create":
            documents_to_insert = []
            for doc in request.data:
                doc = convert_object_ids(doc)
                doc.update({
                    "createdAt": current_datetime,
                    "updatedAt": current_datetime
                })
                documents_to_insert.append(doc)
            result = collection.insert_many(documents_to_insert)
            return {"message": "Records created successfully","inserted_ids": [str(obj_id) for obj_id in result.inserted_ids]}

        if request.action == "update":
            filter_condition = convert_object_ids(request.filter_condition)
            modified_count = 0
            for update_doc in request.data:
                update_doc.update({"updatedAt": current_datetime})
                result = collection.update_many(filter_condition, {"$set": update_doc})
                modified_count += result.modified_count
            return {"message": f"Updated {modified_count} records successfully"}

        if request.action == "delete":
            filter_condition = convert_object_ids(request.filter_condition)
            result = collection.delete_many(filter_condition)
            return {"message": f"Deleted {result.deleted_count} records successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}")