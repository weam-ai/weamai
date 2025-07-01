from src.db.config import db_instance
from pymongo.errors import PyMongoError

class CustomGptDocConfig:
    MAX_TOKEN_LIMIT = 10000
    TOP_K=18

class CustomGptChatConfig:
    MAX_TOKEN_LIMIT = 10000

class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {'gemini-2.0-flash':True, 'gemini-2.5-pro-preview-05-06':True, 'gemini-2.5-flash-preview-04-17':True}
    TEMPRATURE = 0.7
    DEFAUL_GEMINI_1_5_Flash = 'gemini-2.0-flash'
    IMAGE_SIZE_LIST = ["1024x1024","1792x1024","1024x1792","1024x1536","1536x1024"]
    
class GetLLMkey:
    def __init__(self):
        """
        Initialize the repository.

        Args:
            db_instance: An instance of the database.
        """
        self.db_instance = db_instance
        
    def default_llm_key(self,company_id:str = None,query:dict=None,projection:dict=None,companymodel:str = None):
        self.instance = self.db_instance.get_collection(companymodel)
        try:
            result = self.instance.find_one(query,projection)
            if not result:
                raise ValueError(f"No data found for company id: {company_id}")
            return str(result['_id'])
        except PyMongoError as e:
            raise