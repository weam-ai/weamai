from src.db.config import db_instance
from pymongo.errors import PyMongoError

class CustomGptDocConfig:
    MAX_TOKEN_LIMIT = 10000
    TOP_K=18

class CustomGptChatConfig:
    MAX_TOKEN_LIMIT = 10000


class DEFAULTMODEL:
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



class ImageGenerateConfig:
    MAX_TOKEN_LIMIT = 10000
    GPT_4o_MINI = 'gpt-4.1-mini'
    LLM_IMAGE_MODEL = 'dall-e-3'
    DALLE_WRAPPER_SIZE = "1024x1024"
    DALLE_WRAPPER_QUALITY = 'standard'
    DALLE_WRAPPER_STYLE = 'vivid'
    n = 1


class ToolChatConfig:
    MAX_TOKEN_LIMIT = 10000
    VISION_MODELS = {'meta-llama/llama-4-maverick:free': True, 'meta-llama/llama-4-maverick': True, 'meta-llama/llama-4-scout:free': True, 'meta-llama/llama-4-scout': True, 'qwen/qwen3-30b-a3b:free': True}
    TEMPRATURE = 0.7
    DEFAULT_GPT_4o_MINI = 'gpt-4.1-mini'
    IMAGE_SIZE_LIST = ["1024x1024","1792x1024","1024x1792"]
