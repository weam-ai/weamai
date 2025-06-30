from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.abstract_company_repo import CompanyAbstractRepository
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,HF_ERROR_MESSAGES_CONFIG,GENAI_ERROR_MESSAGES_CONFIG,ANTHROPIC_ERROR_MESSAGES_CONFIG, WEAM_ROUTER_MESSAGES_CONFIG

class CompanyRepostiory(CompanyAbstractRepository):
    """Repository for managing threads in a database."""
    def __init__(self):
        """
        Initialize the repository.

        Args:
            db_instance: An instance of the database.
        """
        self.db_instance = db_instance

    def initialization(self, company_id: str, collection_name: str):
        """
        Initialize the repository with thread ID and collection name.

        Args:
            company_id (str): The ID of the thread.
            collection_name (str): The name of the collection.
        """
        self.company_id = company_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result = self._fetch_company_data()
        

    def _fetch_company_data(self):
        """Fetch data related to the thread model."""
        query = {'_id': ObjectId(self.company_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for thread id: {self.company_id}")
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "CompanyRepostiory._fetch_company_data",
                    "api_id": self.company_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "CompanyRepostiory._fetch_company_data",
                    "company_id": self.company_id
                }}
            )

    def update_free_messages(self, model_code):
        """
        Update fields of the company messages.

        Args:
            model_code:code for model to increase message for
        """
        query = {'_id': ObjectId(self.company_id)}
        update = {'$inc': {f'usedFreeMessages.{model_code}': 1}}
        try:
            self.instance.update_one(query, update)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the collection fields: {e}",
                extra={"tags": {
                    "method": "CompanyRepostiory.update_free_messages",
                    "company_id": self.company_id
                }})