from src.custom_lib.langchain.callbacks.huggingface.mongodb.mongodb_handler import MongoDBCallbackHandler
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from src.logger.default_logger import logger

@asynccontextmanager
async def get_mongodb_callback_handler(thread_id: str, chat_history, memory,collection_name,regenerated_flag=False,msgCredit=0,is_paid_user=False) -> AsyncGenerator[MongoDBCallbackHandler, None,]:
    """Get the MongoDB callback handler in a context manager."""
    handler = MongoDBCallbackHandler(thread_id=thread_id, chat_history=chat_history, memory=memory,collection_name=collection_name,regenerated_flag=regenerated_flag,msgCredit=msgCredit,is_paid_user=is_paid_user)
    try:
        yield handler
    except Exception as e:
        logger.error(
            f"Failed to async context manager: {e}",
            extra={"tags": {"method": "mongodb.get_mongodb_callback_handler"}}
        )
        raise e

    
    finally:
        logger.info(
            "MongoDBCallbackHandler cleanup",
            extra={"tags": {"method": "mongodb.get_mongodb_callback_handler"}}
        )