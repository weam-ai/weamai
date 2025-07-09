from datetime import datetime
import pytz
from pymongo.errors import PyMongoError
from src.logger.default_logger import logger
from src.db.config import db_instance
from bson.objectid import ObjectId

def add_notification_data(message, user_data, collection_name) -> str:
    """
    Add a notification to the collection.
    Args:
        notification_data (dict): The notification data to add.
    Returns:
        str: The ID of the inserted notification.
    """
    user_data["id"] = ObjectId(user_data["id"])
    if user_data.get("profile") is not None:
        if user_data.get("profile", {}).get("id") is not None:
            user_data["profile"]["id"] = ObjectId(user_data["profile"]["id"])

    timezone = pytz.timezone("Asia/Kolkata")  # Adjust timezone if needed
    current_datetime = datetime.now(timezone)

    notification_data = {
        "user": user_data,
        "msg": message,
        "isRead": False,  
        "createdAt": current_datetime,
        "updatedAt": current_datetime,
    }
    
    try:
        instance = db_instance.get_collection(collection_name)
        result = instance.insert_one(notification_data)
        logger.info(
            "Successfully added notification to the database",
            extra={"tags": {
                "method": "NotificationRepository.add_notification_data",
                "notification_id": str(result.inserted_id)
            }}
        )
        return str(result.inserted_id)
    except PyMongoError as e:
        logger.error(
            f"An error occurred while adding notification: {e}",
            extra={"tags": {
                "method": "NotificationRepository.add_notification_data"
            }}
        )
        raise