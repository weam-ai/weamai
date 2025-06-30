from typing import List, Optional
import openai
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from fastapi import HTTPException, status
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains.llm import LLMChain
import gc
import json
import asyncio
from src.logger.default_logger import logger
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.tool_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.seo_summaries import SeoRepo
from src.chatflow_langchain.service.pro_agent.config.model_config import DocConfig
from src.chatflow_langchain.service.pro_agent.seo_optimizer.chat_prompt_factory import create_prompt_article
from src.chatflow_langchain.service.pro_agent.seo_optimizer.scraper_articles import ArticleFetcher
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.openai.cost.context_manager import get_custom_openai_callback
from src.custom_lib.langchain.callbacks.openai.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.openai.streaming.custom_stream_async_handler import CustomAsyncIteratorCallbackHandler
from src.chatflow_langchain.service.openai.doc.utils import extract_error_message
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError, NotFoundError
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.service.pro_agent.seo_optimizer.utils import generate_seo_friendly_url
from src.chatflow_langchain.service.config.model_config_openai import OPENAIMODEL,DefaultOpenAIModelRepository

class ArticleGeneratorService:
    def __init__(self):
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
        self.thread_repo = ThreadRepostiory()
        self.article_fetcher=ArticleFetcher()
        self.chat_repository_history = CustomAIMongoDBChatMessageHistory()

    
    async def initialize_chat_input(self,chat_input):
        self.chat_input = chat_input
        self.company_id=chat_input.company_id
        self.thread_id=chat_input.thread_id
        self.thread_model=chat_input.threadmodel
        self.companymodel=chat_input.companymodel
        # self.brain_id=str(ObjectId())
        self.regenerated_flag=chat_input.isregenerated
        # self.chat_session_id=str(ObjectId())
        self.msgCredit=chat_input.msgCredit
        self.is_paid_user=chat_input.is_paid_user
        self.agent_extra_info=chat_input.agent_extra_info
        self.topic=self.agent_extra_info.get("topics","")
        self.delay_chunk=chat_input.delay_chunk


    async def fetch_articles(self): 
       
        self.thread_repo.initialization_thread_id(self.thread_id, collection_name=self.thread_model)
        self.agent_data = self.thread_repo.get_agent_extra_info()
        self.business_summary = self.agent_data.get("business_summary", "No summary provided")
        self.target_audience= self.agent_data.get("target_audience", "Not Specified")
        self.primary_keywords = self.agent_data.get("primary_keywords", [])
        self.secondary_keywords = self.agent_data.get("secondary_keywords", [])
        
        self.location = self.agent_data.get("location", ["United States"])
        self.language = self.agent_data.get("language", "English")
        self.chat_session_id= self.agent_data.get("chat_session_id", None)
        self.brain_id=self.agent_data.get("brain_id", None)
        self.website_url=self.agent_data.get("website_url", None)
        


        await self.article_fetcher.initialize_data(title=self.primary_keywords[0], location=self.location, language=self.language)

        self.article_length,self.top_articles=await self.article_fetcher.get_articles_word_count(title=self.primary_keywords[0])
        self.combined_content=await self.article_fetcher.fetch_article_content_beautifulsoup()
      
    

    async def initialize_llm(self, api_key_id: str = None):
        """
        Initializes the LLM with the specified API key and company model.

        Parameters
        ----------
        api_key_id : str, optional
            The API key ID used for decryption and initialization.
        companymodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:
            self.chat_repository_history = CustomAIMongoDBChatMessageHistory()
            self.api_key_id=DefaultOpenAIModelRepository(self.company_id,self.companymodel).get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(self.api_key_id, self.companymodel)
            self.bot_data = self.llm_apikey_decrypt_service.bot_data
            self.model_name = OPENAIMODEL.MODEL_VERSIONS[self.llm_apikey_decrypt_service.model_name]
            self.custom_handler = CustomAsyncIteratorCallbackHandler()
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.7,
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=True,
                verbose=False,
                stream_usage=True,
                callbacks=[self.custom_handler]

            )
            self.llm_non_stream = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False
            )
            self.llm_sum_memory = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
        
    
    
    async def initialize_repository(self):
        """
        Initializes the chat history repository for data storage.

        Parameters
        ----------
        chat_session_id : str, optional
            The chat session ID for the repository.
        collection_name : str, optional
            The collection name for the repository.

        Exceptions
        ----------
        Logs an error if the repository initialization fails.
        """
        try:
            self.chat_repository_history.initialize(
                chat_session_id=self.chat_session_id,
                collection_name=self.thread_model,
                regenerated_flag=self.regenerated_flag,
                thread_id=self.thread_id
            )
            await self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.initialize_repository"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initalize repository: {e}")

    async def initialize_memory(self):
        """
        Sets up the memory component using ConversationSummaryBufferMemory.

        Exceptions
        ----------
        Logs an error if the memory initialization fails.
        """
        try:
            self.memory = ConversationSummaryBufferMemory(
                memory_key="chat_history",
                input_key="question",
                output_key="answer",
                llm=self.llm_sum_memory,
                max_token_limit=DocConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.initialize_memory"}}
            )

    async def create_prompts(self):
        self.article_prompt = create_prompt_article()
   
    async def create_chain(self):
        """Run the LLM chain to generate content using OpenAI API."""
        try:
            self.article_chain=LLMChain(
                llm=self.llm,
                prompt= self.article_prompt)
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
    
    def perform_thread_operations(self):
        self.final_steps = {
            "$set": {
                "responseModel":OPENAIMODEL.GPT_4_1,
                "proAgentData.step4": {"status":"completed"},
                "model":self.bot_data
            }}
        self.thread_repo.initialization(self.thread_id, collection_name=self.thread_model)
        self.thread_repo.update_fields(data=self.final_steps)

    async def run_chain(self,kwargs={}):
        try:
            cost_callback = CostCalculator()
            seo_friendly_url = generate_seo_friendly_url(self.website_url, self.primary_keywords)

            async with  \
                    get_custom_openai_callback(self.model_name, cost=cost_callback, thread_id=self.thread_id, collection_name=self.thread_model,**kwargs) as cb, \
                    get_mongodb_callback_handler(thread_id=self.thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=self.thread_model,regenerated_flag=self.regenerated_flag,msgCredit=0,is_paid_user=self.is_paid_user) as mongo_handler:
                run = asyncio.create_task(self.article_chain.arun(
                    {"title":self.topic,"primary_keywords":",".join(self.primary_keywords),"business_summary":self.business_summary, \
                     "combined_content":self.combined_content,"target_audience":self.target_audience,"secondary_keywords":",".join(self.secondary_keywords),\
                     "article_length":self.article_length,"seo_friendly_url": seo_friendly_url},callbacks=[cb,mongo_handler]))

                try:
                    async for token in self.custom_handler.aiter():
                        yield f"data: {token.encode('utf-8')}\n\n", 200
                        await asyncio.sleep(self.delay_chunk)
                finally:
                    await run
                    task=await asyncio.to_thread(self.perform_thread_operations)

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.NotFoundError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai(error_code)

            self.llm_apikey_decrypt_service.update_deprecated_status(True)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
 
        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.RateLimitError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
    
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.APIStatusError"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.APIStatusError"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.LengthFinishReasonError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.ContentFilterFinishReasonError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.APITimeoutError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.APIConnectionError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in OPENAI_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.Exception_Try"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.Exception_Try"}})
                    self.thread_repo.initialization(self.thread_id, self.thread_model)
                    self.thread_repo.add_message_openai(error_code)
                    content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
                    yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
                except Exception as e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "StreamingDocumentedChatService.stream_run_conversation.Exception_Except"}})
                    self.thread_repo.initialization(self.thread_id, self)
                    self.thread_repo.add_message_openai("common_response")
                    content = OPENAI_MESSAGES_CONFIG.get("common_response")
                    yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

        finally:
            # Ensure cleanup is always called
            self.cleanup()
            
    async def test(self):
        """
        A simple test method to yield test events.
        """
        yield "event: streaming\ndata: Initial connection established\n\n"
        await asyncio.sleep(0.2)
        
        for words in ['k', 'a', 'b', 'c', 'd']:
            yield f"event: streaming\ndata: {words}\n\n"
            await asyncio.sleep(0.2)

    def cleanup(self):
        """
        Cleans up any resources or state associated with the service.
        """
        try:
            # List of attributes to clean up
            attributes = [
                'llm',
                'llm_non_stream',
                'llm_sum_memory',
                'memory',
                'vectorstore',
                'additional_prompt',
                'conversational_retrieval_chain',
                'inputs',
                'callback_handler',
                'chat_repository_history',
                'qdrant_vector_store',
                'prompt_repo',
                'thread_repo',
                'vector_store_api_decrypt_service',
                'llm_apikey_decrypt_service',
                'cost_calculator'  # Add this if it's used in the service
            ]

            cleaned_up = []
            for attr in attributes:
                if hasattr(self, attr):
                    delattr(self, attr)
                    cleaned_up.append(attr)
            
            # Log the cleanup process
            if cleaned_up:
                logger.info(f"Successfully cleaned up: {', '.join(cleaned_up)}.")
            
            gc.collect()  # Force garbage collection to free memory

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.cleanup"}}
            )

