from abc import ABC, abstractmethod

class AbstractPromptRepository(ABC):
    """
    Abstract base class for repositories.
    """

    @abstractmethod
    def initialization(self, prompt_id: str, collection_name: str):
        """
        Initialize the repository with prompt ID and collection name.

        Args:
            prompt_id (str): The ID of the prompt.
            collection_name (str): The name of the collection.
        """
        pass

    @abstractmethod
    def _fetch_prompt_model_data(self):
        """
        Fetch data related to the prompt model.

        Returns:
            dict: The prompt model data.
        """
        pass

    @abstractmethod
    def get_content(self):
        """
        Get the content from the prompt model data.

        Returns:
            str: The content of the prompt model.
        """
        pass