from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.abstract_chat_session_repository import AbstractChatSessionRepository

class ChatSessionRepository(AbstractChatSessionRepository):
    """Repository for managing chat sessions in a database."""
    def __init__(self):
        """
        Initialize the repository with db instance
        """
        self.db_instance = db_instance

    def initialization(self, chat_session_id: str, collection_name: str):
        """
        Initialize the repository with session ID and collection name.

        Args:
            chat_session_id (str): The ID of the chat session.
            collection_name (str): The name of the collection.
        """
        self.chat_session_id = chat_session_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result = self._fetch_chat_session_model_data()

    def _fetch_chat_session_model_data(self):
        """Fetch data related to the chat session model."""
        query = {'_id': ObjectId(self.chat_session_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for session id: {self.chat_session_id}")
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "ChatSessionRepository._fetch_chat_session_model_data",
                    "chat_chat_session_id": self.chat_session_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "ChatSessionRepository._fetch_chat_session_model_data",
                    "chat_session_id": self.chat_session_id
                }}
            )

    def update_fields(self, data):
        """
        Update fields of the chat session model.

        Args:
            data (dict): Data to update.
        """
        query = {'_id': ObjectId(self.chat_session_id)}
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the collection fields: {e}",
                extra={"tags": {
                    "method": "ChatSessionRepository.update_fields",
                    "chat_session_id": self.chat_session_id
                }}
            )

   