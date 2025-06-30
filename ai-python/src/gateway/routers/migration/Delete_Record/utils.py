from fastapi import APIRouter
from bson import ObjectId
from src.db.config import db_instance
from src.logger.default_logger import logger

router = APIRouter()

# Initialize collections
chat_collection = db_instance.get_collection("chat")
chat_member_collection = db_instance.get_collection("chatMember")
messages_collection = db_instance.get_collection("messages")
importchat_collection = db_instance.get_collection("importChat")


def convert_to_object_ids(ids):
    """Converts a list of string IDs to ObjectId instances if not already an ObjectId."""
    return [ObjectId(chat_id) if not isinstance(chat_id, ObjectId) else chat_id for chat_id in ids]

async def delete_chat_members(chat_ids_list):
    deleted_ids = []
    if chat_ids_list:
        object_ids = convert_to_object_ids(chat_ids_list)
        result = chat_member_collection.delete_many({"chatId": {"$in": object_ids}})
        if result.deleted_count > 0:
            deleted_ids = chat_ids_list
        logger.info(f"Deleted chat members for chat IDs: {deleted_ids}")
    return deleted_ids

async def delete_messages(chat_ids_list):
    deleted_ids = []
    if chat_ids_list:
        object_ids = convert_to_object_ids(chat_ids_list)
        result = messages_collection.delete_many({"chatId": {"$in": object_ids}})
        if result.deleted_count > 0:
            deleted_ids = chat_ids_list
        logger.info(f"Deleted messages for chat IDs: {deleted_ids}")
    return deleted_ids

async def delete_chats(chat_ids_list):
    deleted_ids = []
    if chat_ids_list:
        object_ids = convert_to_object_ids(chat_ids_list)
        result = chat_collection.delete_many({"_id": {"$in": object_ids}})
        if result.deleted_count > 0:
            deleted_ids = chat_ids_list
        logger.info(f"Deleted chats for chat IDs: {deleted_ids}")
    return deleted_ids

async def delete_import_chat(import_id):
    if import_id:
        importchat_collection.delete_one({"_id": ObjectId(import_id)})
        logger.info(f"Deleted chat for chat ID: {import_id}")
    return import_id

async def delete_import_chat_conversationdata(import_id, chat_ids_list):
    deleted_ids = []
    if chat_ids_list:
        unset_query = {f"conversationData.{chat_id}": "" for chat_id in chat_ids_list}
        result = importchat_collection.update_one(
            {"_id": ObjectId(import_id)},
            {"$unset": unset_query}
        )
        if result.modified_count > 0:
            deleted_ids = chat_ids_list
        logger.info(f"Successfully removed chat objects from import ID: {import_id}")
    return deleted_ids

async def delete_failed_records(import_id, chat_ids_list):
    deleted_records = {
        "chat_members": await delete_chat_members(chat_ids_list),
        "messages": await delete_messages(chat_ids_list),
        "chats": await delete_chats(chat_ids_list),
        "import_chats": await delete_import_chat(import_id),
        # "import_chats_conversationdata": await delete_import_chat_conversationdata(import_id, chat_ids_list)
    }
    logger.info(f"Completed deletion of failed records for import ID: {import_id}")
    return deleted_records