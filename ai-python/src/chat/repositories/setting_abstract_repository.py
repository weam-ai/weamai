from abc import ABC, abstractmethod
class SettingAbstractRepository(ABC):
    """Abstract base class for setting repositories."""

    @abstractmethod
    def initialization(self, collection_name):
        """
        Initialize the repository with collection name.

        Args:
            collection_name (str): The name of the collection.
        """
        pass
