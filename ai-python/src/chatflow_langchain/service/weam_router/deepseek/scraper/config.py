from src.db.config import db_instance
from pymongo.errors import PyMongoError

class ScraperConfig:
    SUCCESS_TITLE = "Your prompt {title} from brain {brain_title} is now ready to use!"
    SUCCESS_BODY = "Your prompt {title} from brain {brain_title} is now ready. You can now use this prompt to initiate the desired response."
    FAILURE_TITLE = "Your prompt {title} from brain {brain_title} Preparation Unsuccessful"
    FAILURE_BODY = "We encountered an issue while preparing the prompt {title} from brain {brain_title}. Please review the details and try again. If the problem persists, contact support for further assistance."


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