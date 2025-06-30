from abc import ABC, abstractmethod


class ThreadAbstractRepository(ABC):
    """Abstract base class for thread repositories."""

    @abstractmethod
    def initialization(self, thread_id, collection_name):
        """Initialize the repository with thread ID and collection name.

        Args:
            thread_id (str): The ID of the thread.
            collection_name (str): The name of the collection.
        """
        pass

    @abstractmethod
    def _fetch_thread_model_data(self):
        """Fetch data related to the thread model."""
        pass