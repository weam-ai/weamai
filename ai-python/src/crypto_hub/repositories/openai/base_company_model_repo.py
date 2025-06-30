from abc import ABC, abstractmethod

class AbstractCompanyModelRepository(ABC):
    """
    Abstract base class to enforce implementation of specific methods
    in any subclass that interacts with company model data.
    """

    @abstractmethod
    def initialization(self, api_key_id, collection_name):
        """
        Initializes the object with the provided API key identifier.

        Args:
            api_key_id (str): The API key identifier.
            collection_name (str): The collection name in the database.

        Raises:
            ValueError: If initialization fails due to missing data or other issues.
        """
        pass

    @abstractmethod
    def _fetch_company_model_data(self):
        """
        Fetches the company model data from the database using the API key identifier.

        Returns:
            dict: The company model data.

        Raises:
            ValueError: If no data is found for the given API key identifier.
        """
        pass

    @abstractmethod
    def get_model_name(self):
        """
        Gets the model name from the fetched company model data.

        Returns:
            str: The model name.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        pass

    @abstractmethod
    def _get_config_data(self):
        """
        Gets the config data from the fetched company model data.

        Returns:
            dict: The config data.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        pass