from src.db.config import db_instance
from src.logger.default_logger import logger
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

class OPENAIMODEL:
    GPT_35 = 'gpt-3.5-turbo'
    GPT_4o_MINI = 'gpt-4.1-mini'
    GPT_TEXT_MODEL = "text-embedding-3-small"

class BaseDefaultModelRepository:
    def __init__(self, company_id: str, companymodel: str):
        """
        Initialize the repository with the given company ID and model collection.

        Args:
            company_id (str): The ID of the company.
            companymodel (str): The name of the collection to query.
        """
        self.company_id = company_id
        self.companymodel = companymodel
        self.db_instance = db_instance
    
    def get_collection(self):
        return self.db_instance.get_collection(self.companymodel)
    
    def get_default_model_key(self, query: dict, projection: dict):
        """
        Retrieve the default model key from the database.

        Args:
            query (dict): The query used to find the model.
            projection (dict): The fields to include in the result.
        
        Returns:
            str: The ID of the default model found.
        """
        instance = self.get_collection()
        try:
            result = instance.find_one(query, projection)
            if not result:
                raise ValueError(f"No default model found for company id: {self.company_id} in {self.companymodel}")
            return str(result['_id'])
        except PyMongoError as e:
            logger.error(f"Database query failed for company id {self.company_id}: {e}")
            raise

class DefaultGPT35ModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": OPENAIMODEL.GPT_35,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)

class DefaultGPT4oMiniModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": OPENAIMODEL.GPT_4o_MINI,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)

class DefaultGPTTextModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": OPENAIMODEL.GPT_TEXT_MODEL,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)

class OutSideDefaultGPTTextModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": OPENAIMODEL.GPT_TEXT_MODEL,
            "company.id": ObjectId(self.company_id)
        }
        projection = {"_id": 1, "deletedAt": 1}
        instance = self.get_collection()
        try:
            self.result = instance.find_one(query, projection)
            if not self.result:
                raise ValueError(f"No default model found for company id: {self.company_id} in {self.companymodel}")
            
            if self.check_deleted_key():
                raise ValueError(f"The model for company id {self.company_id} has been deleted.")
            
            return str(self.result['_id'])
        except PyMongoError as e:
            logger.error(f"Database query failed for company id {self.company_id}: {e}")
            raise

    def check_deleted_key(self):
        """
        Checks if the 'deletedAt' key exists in the result data.

        Returns:
            bool: True if the 'deletedAt' key exists and has a value, False otherwise.
        """
        value_check = self.result.get("deletedAt")
        return bool(value_check)

class DefaultModelNotFoundException(Exception):
    def __init__(self, company_id, company_model):
        self.company_id = company_id
        self.company_model = company_model
        self.message = f"No default model found for company id: {company_id} in {company_model}"
        super().__init__(self.message)