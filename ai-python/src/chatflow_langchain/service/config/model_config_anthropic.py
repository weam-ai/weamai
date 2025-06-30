from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.chatflow_langchain.service.config.baseModel_repository import BaseDefaultModelRepository
class ANTHROPICMODEL:
    CLAUDE_SONNET_3_5='claude-3-5-sonnet-latest'
    CLAUDE_SONNET_3_7='claude-3-7-sonnet-latest'
    CLAUDE_HAIKU_3_5 ='claude-3-5-haiku-latest'
    DEFAULT_TOOL_MODEL = 'claude-3-5-haiku-latest'
    MAX_TOKEN_LIMIT_CONFIG = {
        'claude-3-5-sonnet-latest':8192,
        'claude-3-5-haiku-latest':8192,
        'claude-3-opus-latest':4096,
        'claude-3-sonnet-20240229':4096,
        'claude-3-haiku-20240307':4096,
        'claude-3-7-sonnet-latest':64000,
        'claude-opus-4-20250514':32000,
        'claude-sonnet-4-20250514':64000,
    }
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

class Functionality:
    CHAT = 'CHAT'
    AGENT = 'AGENT'
    
class DefaultSonnet35ModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": ANTHROPICMODEL.CLAUDE_SONNET_3_5,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)
   
class DefaultAnthropicModelRepository(BaseDefaultModelRepository):
    def get_default_model_key(self):
        query = {
            "name": ANTHROPICMODEL.CLAUDE_HAIKU_3_5,
            "company.id": ObjectId(self.company_id)
        }
        projection = {'_id': 1}
        return super().get_default_model_key(query, projection)
