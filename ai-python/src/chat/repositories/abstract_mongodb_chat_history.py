from typing import List, Union, Sequence, Dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from abc import ABC, abstractmethod

# Default database and collection names
DEFAULT_DBNAME = "customai"
DEFAULT_COLLECTION_NAME = "messages"



class AbstractChatMessageHistory(BaseChatMessageHistory, ABC):
    @abstractmethod
    def initialize(self, connection_string: str, chat_session_id: str, database_name: str = DEFAULT_DBNAME, collection_name: str = DEFAULT_COLLECTION_NAME) -> None:
        """
        Initialize the database connection and collection.

        Args:
            connection_string (str): The MongoDB connection string.
            chat_session_id (str): The chat session identifier.
            database_name (str): The name of the database.
            collection_name (str): The name of the collection.
        """
        pass

    @abstractmethod
    def _retrieve_messages_from_db(self) -> List[Dict]:
        """
        Retrieve messages from the database.

        Returns:
            List[Dict]: List of retrieved messages.
        """
        pass

    @abstractmethod
    def _extract_messages(self, result_list: List[Dict]) -> List[Dict]:
        """
        Extract messages from the result list.

        Args:
            result_list (List[Dict]): List of result dictionaries.

        Returns:
            List[Dict]: List of extracted messages.
        """
        pass

    @abstractmethod
    def _parse_messages(self, messages: List[Dict]) -> List[BaseMessage]:
        """
        Parse messages from the extracted messages.

        Args:
            messages (List[Dict]): List of extracted messages.

        Returns:
            List[BaseMessage]: List of parsed messages.
        """
        pass

    @abstractmethod
    def add_message(self, message: Union[BaseMessage, str], thread_id: str, message_type: str) -> None:
        """
        Add a message to the database.

        Args:
            message (Union[BaseMessage, str]): The message to add.
            thread_id (str): The thread identifier.
            message_type (str): The type of message ('system' or 'ai').
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all messages for the current chat session.
        """
        pass

    @abstractmethod
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """
        Add multiple messages to the database.

        Args:
            messages (Sequence[BaseMessage]): The messages to add.
        """
        pass

    @property
    @abstractmethod
    def messages(self) -> List[BaseMessage]:
        """
        Get the list of messages.

        Returns:
            List[BaseMessage]: List of messages.
        """
        pass
