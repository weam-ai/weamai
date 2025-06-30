from abc import ABC, abstractmethod
class FileAbstractRepository(ABC):
    """Abstract base class for file repositories."""

    @abstractmethod
    def initialization(self, file_id, collection_name):
        """
        Initialize the repository with file ID and collection name.

        Args:
            file_id (str): The ID of the file.
            collection_name (str): The name of the collection.
        """
        pass

    @abstractmethod
    def _fetch_file_model_data(self):
        """Fetch data related to the file model."""
        pass