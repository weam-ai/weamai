from src.db.config import db_instance
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.crypto_hub.repositories.openai.base_company_model_repo import AbstractCompanyModelRepository
from src.logger.default_logger import logger


class EmbeddingModelRepository(AbstractCompanyModelRepository):
    """
    Repository class to interact with the company model data in the database.
    """

    def __init__(self):
        """
        Initializes the CompanyModelRepository with the given database instance.
        """
        self.db_instance = db_instance

    def initialization(self, api_key_id, collection_name):
        """
        Initializes the object with the provided API key identifier.

        Args:
            api_key_id (str): The API key identifier.
            collection_name (str): The collection name in the database.

        Raises:
            ValueError: If initialization fails due to missing data or other issues.
        """
        self.api_key_id = api_key_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result = self._fetch_company_model_data()

    def _fetch_company_model_data(self):
        """
        Fetches the company model data from the database using the API key identifier.

        Returns:
            dict: The company model data.

        Raises:
            ValueError: If no data is found for the given API key identifier.
        """
        query = {"_id": ObjectId(self.api_key_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for API key: {self.api_key_id}")
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "EmbeddingModelRepository._fetch_company_model_data",
                    "api_id": self.api_key_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "EmbeddingModelRepository._fetch_company_model_data",
                    "api_id": self.api_key_id
                }}
            )

    def get_model_name(self):
        """
        Gets the model name from the fetched company model data.

        Returns:
            str: The model name.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        try:
            return self.result['name']
        except KeyError as e:
            logger.error(
                f"Key error while getting model name: {e}",
                extra={"tags": {
                    "method": "EmbeddingModelRepository.get_model_name",
                    "api_id": self.api_key_id
                }}
            )
            raise KeyError(f"Key error while getting model name: {e}")

    def get_dimensions(self):
        """
        Gets the dimensions from the fetched company model data.

        Returns:
            dict: The dimensions data.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        try:
            return self.result.get('dimensions',1536)
        except KeyError as e:
            logger.error(
                f"Key error while getting dimensions: {e}",
                extra={"tags": {
                    "method": "EmbeddingModelRepository.get_dimensions",
                    "api_id": self.api_key_id
                }}
            )
            raise KeyError(f"Key error while getting dimensions: {e}")

    def _get_config_data(self):
        """
        Gets the config data from the fetched company model data.

        Returns:
            dict: The config data.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        try:
            return self.result['config']
        except KeyError as e:
            logger.error(
                f"Key error while getting config data: {e}",
                extra={"tags": {
                    "method": "EmbeddingModelRepository._get_config_data",
                    "api_id": self.api_key_id
                }}
            )
            raise KeyError(f"Key error while getting config data: {e}")
