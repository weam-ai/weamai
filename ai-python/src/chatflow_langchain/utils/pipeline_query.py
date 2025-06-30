from bson.objectid import ObjectId
from typing import List, Dict

def get_latest_checkpoint(chat_session_id: str, db) -> int:
    """
    Get the latest sumhistory_checkpoint value for a given chat session ID.

    Args:
        chat_session_id (str): Chat session identifier.
        db (Database): MongoDB database object.

    Returns:
        int: Latest sumhistory_checkpoint value.
    """
    latest_checkpoint_pipeline = [
        {
            "$match": {
                "chat_session_id": ObjectId(chat_session_id),
            }
        },
        {
            "$project": {
                "_id": 0,
                "sumhistory_checkpoint": 1,
                "createdAt": 1
            }
        },
        {
            "$sort": { "createdAt": -1 }
        },
    ]
    result = list(db.messages.aggregate(latest_checkpoint_pipeline))
    return result[1].get("sumhistory_checkpoint",None) if len(result) > 1 else None


def get_pipeline_v2(chat_session_id: str, latest_checkpoint: int) -> List[Dict]:
    """
    Generate the pipeline for MongoDB aggregation.

    Args:
        chat_session_id (str): Chat session identifier.
        latest_checkpoint (int): Latest sumhistory_checkpoint value.

    Returns:
        List[Dict]: Aggregation pipeline.
    """
    return [
        {
            "$match": {
                "chat_session_id": ObjectId(chat_session_id),
                "system": {"$ne": None},
                "message": {"$ne": None},
                "ai": {"$ne": None},
                "createdAt": { "$ne": None },
                "sumhistory_checkpoint": latest_checkpoint
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "system": {"$first": '$system'},
                "img_gen_prompt": { "$first": "$img_gen_prompt" },
                "message": {"$first": '$message'},
                "ai": {"$first": '$ai'},
                "chat_session_id": {"$first": '$chat_session_id'},
                "sumhistory_checkpoint": {"$first": "$sumhistory_checkpoint"},
                "createdAt": { "$first": "$createdAt" }
            }
        },
        {
            "$sort": { "createdAt": 1 }
        }
    ]


def retrieve_thread_checkpoint(thread_id: str, db) -> int:
    """
    Get the latest sumhistory_checkpoint value for a given chat session ID.

    Args:
        thread_id (str): Thread Id identifier.
        db (Database): MongoDB database object.

    Returns:
        int: Latest sumhistory_checkpoint value.
    """
    latest_checkpoint_pipeline = [
        {
            "$match": {
                "_id": ObjectId(thread_id),
                "system": { "$ne": None },
                "message": { "$ne": None },
                "ai": { "$ne": None }
            }
        },
        {
            "$group": {
                "_id": "$chat_session_id",
                "lastDocument": { "$last": "$$ROOT" }
            }
        },
        {
            "$replaceRoot": { "newRoot": "$lastDocument" }
        },
        {
            "$project": {
                "_id": 0,
                "sumhistory_checkpoint": 1,
                "createdAt":2
            }
        },
        {
            "$sort": { "createdAt": -1 }
        },
    ]
    result = list(db.messages.aggregate(latest_checkpoint_pipeline))
    latest_checkpoint = result[0].get("sumhistory_checkpoint",None) if result else None
    createdAt = result[0].get("createdAt",None) if result else None
    return latest_checkpoint,createdAt

def regenerate_history_pipeline(chat_session_id: str, latest_checkpoint: str,createdAt):

    return [
  {
    "$match": {
      "chat_session_id": ObjectId(chat_session_id),
      "sumhistory_checkpoint": latest_checkpoint,
      "createdAt": { "$lte": createdAt }
    }
  },
  {
            "$group": {
                "_id": "$_id",
                "system": {"$first": '$system'},
                "message": {"$first": '$message'},
                "img_gen_prompt": { "$first": "$img_gen_prompt" },
                "ai": {"$first": '$ai'},
                "chat_session_id": {"$first": '$chat_session_id'},
                "sumhistory_checkpoint": {"$first": "$sumhistory_checkpoint"},
                "createdAt": { "$first": "$createdAt" }
            }
        },
  {
    "$sort": { "createdAt": 1 }  
  }
]