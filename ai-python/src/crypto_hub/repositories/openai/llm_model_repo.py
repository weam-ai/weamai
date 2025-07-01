from src.db.config import db_instance
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.crypto_hub.repositories.openai.base_company_model_repo import AbstractCompanyModelRepository
from src.logger.default_logger import logger

class LLMModelRepository(AbstractCompanyModelRepository):
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
        self.collection_name = collection_name

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
                    "method": "LLMModelRepository._fetch_company_model_data",
                    "api_id": self.api_key_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository._fetch_company_model_data",
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
                    "method": "LLMModelRepository.get_model_name",
                    "api_id": self.api_key_id
                }}
            )
            raise KeyError(f"Key error while getting model name: {e}")
        
    def get_task_type(self):
        """
        Gets the Task Type from the fetched company model data.

        Returns:
            str: Task Type.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        try:
            return self.result['taskType']
        except KeyError as e:
            logger.error(
                f"Key error while getting model name: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.get_taskType",
                }}
            )
            raise KeyError(f"Key error while getting model name: {e}")

    def get_bot_data(self):
        """
        Gets the bot data from the fetched company model data.

        Returns:
            dict: The bot data.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        try:
            return self.result['bot']
        except KeyError as e:
            logger.error(
                f"Key error while getting bot data: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.get_bot_data",
                    "api_id": self.api_key_id
                }}
            )
            raise KeyError(f"Key error while getting bot data: {e}")

    def get_extra_config(self):
        """
        Gets the extra config from the fetched company model data.

        Returns:
            dict: The extra_config data.

        Raises:
            KeyError: If the required keys are not present in the data.
        """
        try:
            return self.result['extraConfig']
        except KeyError as e:
            logger.error(
                f"Key error while getting extra_config: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.get_extra_config",
                    "api_id": self.api_key_id
                }}
            )
            raise KeyError(f"Key error while getting extra_config: {e}")

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
                    "method": "LLMModelRepository._get_config_data",
                    "api_id": self.api_key_id
                }}
            )
            raise KeyError(f"Key error while getting config data: {e}")
        
    def tool_enable(self):
        """
        Checks if a tool call is enabled based on the result data.

        This method retrieves the 'toolCall' key from the `result` dictionary 
        to determine if a tool call is enabled. If the key is present and has a 
        truthy value, it returns `True`. Otherwise, it returns `False`.

        Returns:
            bool: `True` if 'toolCall' is enabled, otherwise `False`.

        Raises:
            AttributeError: If there is an issue accessing the 'toolCall' attribute.
            Exception: For any other unexpected errors that occur.
        """
        try:
            toolCall = self.result.get('tool', None)
            if toolCall:
                return True
            else:
                return False
        except AttributeError as e:
            logger.error(
                f"Attribute error while accessing 'toolCall': {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.func_enable",
                    "api_id": self.api_key_id
                }}
            )
            raise AttributeError(f"Attribute error while accessing 'toolCall': {e}")
        except Exception as e:
            logger.error(
                f"An unexpected error occurred: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.func_enable",
                    "api_id": self.api_key_id
                }}
            )
            raise Exception(f"An unexpected error occurred: {e}")


    def vision_enable(self):
        """
        Checks if vision functionality is enabled based on the result data.

        This method retrieves the 'visionEnable' key from the `result` dictionary 
        to determine if vision functionality is enabled. If the key is present and 
        has a truthy value, it returns `True`. Otherwise, it returns `False`.

        Returns:
            bool: `True` if vision functionality is enabled, otherwise `False`.

        Raises:
            AttributeError: If there is an issue accessing the 'visionEnable' attribute.
            Exception: For any other unexpected errors that occur.
        """
        try:
            vision = self.result.get('visionEnable', None)
            if vision:
                return True
            else:
                return False
        except AttributeError as e:
            logger.error(
                f"Attribute error while accessing 'visionEnable': {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.func_enable",
                    "api_id": self.api_key_id
                }}
            )
            raise AttributeError(f"Attribute error while accessing 'visionEnable': {e}")
        except Exception as e:
            logger.error(
                f"An unexpected error occurred: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.func_enable",
                    "api_id": self.api_key_id
                }}
            )
            raise Exception(f"An unexpected error occurred: {e}")
        
    def stream_enable(self):
        """
        Checks if vision functionality is enabled based on the result data.

        This method retrieves the 'visionEnable' key from the `result` dictionary 
        to determine if vision functionality is enabled. If the key is present and 
        has a truthy value, it returns `True`. Otherwise, it returns `False`.

        Returns:
            bool: `True` if vision functionality is enabled, otherwise `False`.

        Raises:
            AttributeError: If there is an issue accessing the 'visionEnable' attribute.
            Exception: For any other unexpected errors that occur.
        """
        try:
            vision = self.result.get('stream', None)
            if vision:
                return True
            else:
                return False
        except AttributeError as e:
            logger.error(
                f"Attribute error while accessing 'visionEnable': {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.func_enable",
                    "api_id": self.api_key_id
                }}
            )
            raise AttributeError(f"Attribute error while accessing 'visionEnable': {e}")
        except Exception as e:
            logger.error(
                f"An unexpected error occurred: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.func_enable",
                    "api_id": self.api_key_id
                }}
            )
            raise Exception(f"An unexpected error occurred: {e}")
        
    def get_companyKeys(self, company_id):
        """
        Fetches company keys based on the company ID and functionality.

        Args:
            company_id (str): The ID of the company.
            functionality (str): The functionality to filter.

        Returns:
            list: A list of company keys.

        Raises:
            ValueError: If no data is found for the given company ID and functionality.
        """
        try:

            query = {"code": "ROUND_ROBIN", "company.id": company_id}
            projection = {"_id": 0,"company.id": 1, "companyKeys": 1}
            result = self.db_instance[self.collection_name].find_one(query, projection)
            company_keys = result.get('companyKeys',False)
            # if not company_keys:
            #     raise ValueError(f"No company keys found for company ID: {company_id}")
            return company_keys
        except PyMongoError as e:
            logger.error(
                f"An error occurred while fetching company keys: {e}",
                extra={"tags": {
                    "method": "LLMModelRepository.get_companyKeys",
                    "company_id": company_id
                }}
            )
            raise