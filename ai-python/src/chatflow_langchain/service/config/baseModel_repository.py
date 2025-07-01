from src.db.config import db_instance
from src.logger.default_logger import logger
from pymongo.errors import PyMongoError

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