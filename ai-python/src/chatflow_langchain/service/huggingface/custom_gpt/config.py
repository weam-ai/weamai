from src.db.config import db_instance
from pymongo.errors import PyMongoError

class CustomGptDocConfig:
    MAX_TOKEN_LIMIT = 10000
    TOP_K=18
    MAX_TOTAL_TOKENS = 4096

class CustomGptChatConfig:
    MAX_TOKEN_LIMIT = 10000
    MAX_TOTAL_TOKENS = 4096


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