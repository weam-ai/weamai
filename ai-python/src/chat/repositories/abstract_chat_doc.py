from abc import ABC, abstractmethod

class AbstractChatDocsRepository(ABC):
    """Abstract base class for managing chat documents in a database."""
    
    @abstractmethod
    def initialization(self, file_id_list: list, collection_name: str):
        """
        Initialize the repository with a list of file IDs and collection name.

        Args:
            file_id_list (list): The list of file IDs.
            collection_name (str): The name of the collection.
        """
        pass

    @abstractmethod
    def _fetch_chat_docs_model_data(self):
        """Fetch data related to the chat member model."""
        pass
