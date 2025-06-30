from typing import Any, Dict, List
from langchain.callbacks.base import AsyncCallbackHandler
import msgpack
from src.logger.default_logger import logger
from langchain.schema import LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.callbacks.perplexity.mongodb.utils import replace_citations
from langchain_community.callbacks.manager import get_openai_callback
from src.chatflow_langchain.service.perplexity.browser_chat.utils import filter_valid_images
from src.chatflow_langchain.repositories.company_repository import CompanyRepostiory
from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_openai import Functionality
company_repo=CompanyRepostiory()
thread_repo=ThreadRepostiory()
class MongoDBCallbackHandler(AsyncCallbackHandler):
    def __init__(self, thread_id: str = None, chat_history: str = None, memory=None,collection_name=None,regenerated_flag=False,model_name=None,msgCredit=0,is_paid_user=False,**kwargs):
        self.thread_id = thread_id
        self.chat_history = chat_history
        self.memory = memory
        self.stream_flag = False
        self.collection_name=collection_name
        self.regenerated_flag = regenerated_flag
        self.model_name =model_name
        self.msgCredit = msgCredit
        self.is_paid_user = is_paid_user
        self.encrypted_key = kwargs.get('encrypted_key',None)
        self.companyRedis_id=kwargs.get('companyRedis_id','default')
        
    async def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Dict[str, Any]]], **kwargs: Any) -> None:
        pass
    
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token is not None and token != "":
            self.stream_flag = True

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        try:
            api_usage_service  = APIKeyUsageService()
            self.messages = ''
            if self.stream_flag:
                citations = list(dict.fromkeys(response.generations[0][0].generation_info['citations']))
                images = list({obj['image_url']: obj for obj in response.generations[0][0].generation_info['images']}.values())
                for generation_list in response.generations:
                    for generation in generation_list:
                        self.messages += generation.text
                valid_images = await filter_valid_images(images) 
                self.messages = await replace_citations(self.messages, citations)     
                self.chat_history.add_ai_message_kwargs(
                    message=self.messages,
                    thread_id=self.thread_id,
                    citations=citations,
                    images=valid_images
                )
                thread_repo.initialization(thread_id=self.thread_id,collection_name=self.collection_name)
                if self.is_paid_user:
                    thread_repo.update_credits(msgCredit=self.msgCredit)
                else:
                    company_repo.initialization(company_id=str(thread_repo.result['companyId']),collection_name='company')
                    company_repo.update_free_messages(model_code='PERPLEXITY')
                if not self.regenerated_flag:
                    with get_openai_callback() as cb:
                        self.memory.prune()
                    # await api_usage_service.update_usage(provider='OPEN_AI',tokens_used= cb.total_tokens, model=self.memory.llm.model_name, api_key=self.encrypted_key,functionality=Functionality.CHAT,company_id=self.companyRedis_id)    
                    thread_repo.update_token_usage_summary(cb=cb)
                    self.chat_history.add_message_system(
                        message=self.memory.moving_summary_buffer,
                        thread_id=self.thread_id
                    )
                else: 
                    thread_repo.update_response_model(responseModel=self.model_name,model_code='PERPLEXITY')
                logger.info(
                    "Successfully stored the response",
                    extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_end"}}
                )
            else:
                logger.info(
                    "LLM response was condensed, no storage needed",
                    extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_end"}}
                )
        except Exception as e:
            logger.error(
                "Error processing LLM response",
                exc_info=True,
                extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_end", "exception": str(e)}}
            )
            raise e

    async def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        logger.error(
            "Error encountered during LLM execution",
            exc_info=True,
            extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_error", "exception": str(error)}}
        )
        pass