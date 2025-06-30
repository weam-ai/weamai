from src.db.config import db_instance
from pymongo.errors import PyMongoError

class CustomGptDocConfig:
    MAX_TOKEN_LIMIT = 10000
    TOP_K=18

class CustomGptChatConfig:
    MAX_TOKEN_LIMIT = 10000

class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {
                    'claude-3-5-sonnet-latest': True,
                     'claude-3-5-sonnet-20241022':True,
                     'claude-3-opus-20240229':True,
                     'claude-3-sonnet-20240229':True,
                     'claude-3-haiku-20240307':True,
                     'claude-3-opus-latest':True,
                     'claude-3-7-sonnet-latest':True,
                     'claude-3-5-haiku-latest':True,
                     'claude-opus-4-20250514':True,
                     'claude-sonnet-4-20250514':True
                     }
    TEMPRATURE = 0.7
    DEFAULT_GPT_4o_MINI = 'gpt-4.1-mini'
    DEFAULT_ANTHROPIC_SONNET = 'claude-3-5-sonnet-latest'
    IMAGE_SIZE_LIST = ["1024x1024","1792x1024","1024x1792","1024x1536","1536x1024"]


class DEFAULTMODEL:
      GPT_35="gpt-3.5-turbo"
      GPT_4o_MINI ='gpt-4.1-mini'
    
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