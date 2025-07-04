import os
from src.db.config import db_instance
from src.logger.default_logger import logger
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.crypto_hub.utils.crypto_utils import crypto_service

class OPENAIMODEL:
    GPT_4o_MINI = 'gpt-4.1-mini'
    GPT_4o = 'gpt-4.1'
    GPT_TEXT_MODEL = "text-embedding-3-small"
    MODEL_VERSIONS = {
                    'gpt-4.1': 'gpt-4.1',
                    'gpt-4.1-mini': 'gpt-4.1-mini',
                    'gpt-4.1-nano': 'gpt-4.1-nano',
                    'gpt-4o':'gpt-4o-2024-11-20',
                      }

class GEMINIMODEL:
    GEMINI_2O_FLASH= 'gemini-2.0-flash'


class DocConfig:
    MAX_TOKEN_LIMIT = 10000
    TOP_K = 18


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

class DefaultGPT4oMiniModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": OPENAIMODEL.GPT_4o_MINI,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)

class DefaultGPT4oModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": OPENAIMODEL.GPT_4o,
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
    




class DefaultGemini2oFlashModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": GEMINIMODEL.GEMINI_2O_FLASH,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)
    
    def get_encrypt_key(self) -> str:
        """
        Decrypt the provided key using the company's encryption method.


        Returns:
            str: The decrypted key.
        """
        query = {
            "name": GEMINIMODEL.GEMINI_2O_FLASH,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'config.apikey': 1}

        self.response = self.get_collection().find_one(query, projection)
         
        # Placeholder for decryption logic
        self.encrypt_key=self.response.get("config","").get("apikey","")
        # Replace with actual decryption code
        return self.encrypt_key
    def get_decrypt_key(self) -> str:
        """
        Decrypt the encrypted key retrieved from the database.

        This method uses the decryptor to decrypt the encrypted key 
        fetched from the database for the specified company and model.

        Returns:
            str: The decrypted key.
        """
      
        
        try:
            decrypted_key = crypto_service.decrypt(self.encrypt_key)
            return decrypted_key
        except Exception as e:
            logger.error(f"Failed to decrypt the key for company id {self.company_id}: {e}")

       
