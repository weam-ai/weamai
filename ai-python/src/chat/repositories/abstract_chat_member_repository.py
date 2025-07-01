from abc import ABC, abstractmethod
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.logger.default_logger import logger

class AbstractChatMemberRepository(ABC):
    """Repository for managing chat sessions in a database."""
    
    @abstractmethod
    def initialization(self, chat_session_id: str, collection_name: str):
        """
        Initialize the repository with session ID and collection name.

        Args:
            chat_session_id (str): The ID of the chat session.
            collection_name (str): The name of the collection.
        """
        pass

    @abstractmethod
    def _fetch_chat_member_model_data(self):
        """Fetch data related to the chat session model."""
        query = {'_id': ObjectId(self.chat_session_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for session id: {self.chat_session_id}")
            logger.info(
                "Successfully accessed the database",
                extra={"tags": {
                    "method": "ChatSessionRepository._fetch_chat_session_model_data",
                    "chat_session_id": self.chat_session_id
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



  
