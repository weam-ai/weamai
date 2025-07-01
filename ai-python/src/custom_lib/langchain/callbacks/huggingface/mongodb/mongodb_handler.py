from typing import Any, Dict, List
from langchain.callbacks.base import AsyncCallbackHandler
from src.logger.default_logger import logger
from langchain.schema import LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.callbacks.huggingface.cost.context_manager import get_huggingface_callback
from src.chatflow_langchain.repositories.company_repository import CompanyRepostiory
company_repo=CompanyRepostiory()
thread_repo=ThreadRepostiory()

class MongoDBCallbackHandler(AsyncCallbackHandler):
    def __init__(self, thread_id: str = None, chat_history: str = None, memory=None,collection_name=None,regenerated_flag=False,msgCredit=0,is_paid_user=False):
        self.thread_id = thread_id
        self.chat_history = chat_history
        self.memory = memory
        self.stream_flag = False
        self.collection_name=collection_name
        self.regenerated_flag = regenerated_flag
        self.msgCredit = msgCredit
        self.is_paid_user=is_paid_user
        
    async def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Dict[str, Any]]], **kwargs: Any) -> None:
        pass
    
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token is not None and token != "":
            self.stream_flag = True

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        try:
            self.messages = ''
            if self.stream_flag:
                for generation_list in response.generations:
                    for generation in generation_list:
                        self.messages += generation.text
                self.chat_history.add_ai_message(
                    message=self.messages,
                    thread_id=self.thread_id
                )
                thread_repo.initialization(thread_id=self.thread_id,collection_name=self.collection_name)
                if self.is_paid_user:
                    thread_repo.update_credits(msgCredit=self.msgCredit)
                else:
                    company_repo.initialization(company_id=str(thread_repo.result['companyId']),collection_name='company')
                    company_repo.update_free_messages(model_code='HUGGING_FACE')
                if not self.regenerated_flag:
                    with get_huggingface_callback() as cb:
                        self.memory.prune()

                    thread_repo.update_token_usage_summary(cb=cb)
                    self.chat_history.add_message_system(
                        message=self.memory.moving_summary_buffer,
                        thread_id=self.thread_id
                    )
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
