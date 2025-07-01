
import json
from typing import List
from redis import Redis, RedisError
from pymongo import MongoClient, errors
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)
from src.chat.repositories.abstract_mongodb_chat_history import AbstractChatMessageHistory
from src.logger.default_logger import logger

DEFAULT_DB_NAME = "chat_history"
DEFAULT_COLLECTION_NAME = "message_store"

MAX_MESSAGES = 50  # Limit for conversation history


class RedisMongoDBChatMessageHistory(AbstractChatMessageHistory):
    """Chat message history with primary storage in Redis and secondary in MongoDB."""
    
    def __init__(
        self,
        redis_connection: str,
        mongo_connection: str,
        session_id: str,
        redis_db: int = 0,
        mongo_db_name: str = DEFAULT_DB_NAME,
        mongo_collection_name: str = DEFAULT_COLLECTION_NAME,
        ttl: int = None,  # Time-to-live in seconds for Redis key (optional)
    ):
        super().__init__()  # Call the parent class initializer
        self.session_id = session_id
        self.redis_db = redis_db
        self.mongo_db_name = mongo_db_name
        self.mongo_collection_name = mongo_collection_name
        self.ttl = ttl
        
        self.redis_client = self._connect_redis(redis_connection, redis_db)
        self.mongo_collection = self._connect_mongo(mongo_connection, mongo_db_name, mongo_collection_name)

    def _connect_redis(self, connection_string: str, db: int) -> Redis:
        """Establish a connection to Redis."""
        try:
            return Redis.from_url(connection_string, db=db, decode_responses=True)
        except RedisError as error:
            logger.error(
                f"Redis connection error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory._connect_redis"}}
            )
            raise

    def _connect_mongo(self, connection_string: str, db_name: str, collection_name: str) -> MongoClient:
        """Establish a connection to MongoDB."""
        try:
            client = MongoClient(connection_string)
            db = client[db_name]
            collection = db[collection_name]
            return collection
        except errors.ConnectionFailure as error:
            logger.error(
                f"MongoDB connection error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory._connect_mongo"}}
            )
            raise

    def add_message(self, message: BaseMessage) -> None:
        """Add message to Redis and MongoDB, limiting to 50 messages."""
        try:
            history = self.messages
            history.append(message)

            limited_history = history[-MAX_MESSAGES:]

            self._cache_in_redis(limited_history)
            self.mongo_collection.insert_one(
                {
                    "SessionId": self.session_id,
                    "History": json.dumps(message_to_dict(message)),
                }
            )
        except RedisError as error:
            logger.error(
                f"Redis write error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory.add_message"}}
            )
        except errors.WriteError as error:
            logger.error(
                f"MongoDB write error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory.add_message"}}
            )

    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from Redis or MongoDB, limited to 50."""
        try:
            history_json = self.redis_client.get(self.session_id)

            if history_json:
                items = json.loads(history_json)[-MAX_MESSAGES:]  # Last 50 messages
                self._reset_ttl()
            else:
                items = self._fetch_from_mongo()
            
            return messages_from_dict(items)

        except RedisError as error:
            logger.error(
                f"Redis read error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory.messages"}}
            )
            return []
        except errors.OperationFailure as error:
            logger.error(
                f"MongoDB read error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory.messages"}}
            )
            return []

    def _fetch_from_mongo(self) -> List[BaseMessage]:
        """Fetch from MongoDB and cache in Redis, limited to 50 messages."""
        cursor = self.mongo_collection.find({"SessionId": self.session_id}).sort("_id", 1)
        items = [json.loads(doc["History"]) for doc in cursor][-MAX_MESSAGES:]

        self._cache_in_redis(items)

        return items

    def _cache_in_redis(self, messages: List[BaseMessage]) -> None:
        """Cache in Redis with optional TTL."""
        self.redis_client.set(
            self.session_id,
            json.dumps([message_to_dict(m) for m in messages]),
        )
        if self.ttl is not None:
            self.redis_client.expire(self.session_id, self.ttl)

    def _reset_ttl(self) -> None:
        """Reset TTL for the Redis key."""
        if self.ttl is not None:
            self.redis_client.expire(self.session_id, self.ttl)

    def clear(self) -> None:
        """Clear session memory from Redis and MongoDB."""
        try:
            self.redis_client.delete(self.session_id)
            self.mongo_collection.delete_many({"SessionId": self.session_id})
        except RedisError as error:
            logger.error(
                f"Redis delete error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory.clear"}}
            )
        except errors.WriteError as error:
            logger.error(
                f"MongoDB delete error: {error}",
                extra={"tags": {"method": "RedisMongoDBChatMessageHistory.clear"}}
            )
