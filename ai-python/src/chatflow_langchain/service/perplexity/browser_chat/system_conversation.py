import asyncio
import json
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from src.custom_lib.langchain.chat_models.perplexity import ChatPerplexity
from langchain.memory import ConversationSummaryBufferMemory
from typing import AsyncGenerator
from src.logger.default_logger import logger
from src.chat.service.base.abstract_conversation_service import AbstractConversationService
from src.vector_store.qdrant.langchain_lib.qdrant_store import QdrantVectorStoreService
from src.chatflow_langchain.service.perplexity.browser_chat.chat_prompt_factory import create_chat_prompt
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.file_repository import FileRepository
from src.chatflow_langchain.repositories.langchain_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.crypto_hub.services.perplexity.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler as OpenAILLMAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.perplexity.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.perplexity.cost.context_manager import perplexity_async_cost_handler
from src.custom_lib.langchain.callbacks.openai.streaming.custom_stream_async_handler import CustomAsyncIteratorCallbackHandler
from src.chatflow_langchain.service.perplexity.browser_chat.config import BrowserChatConfig
from src.chatflow_langchain.utils.fill_additional_prompt import fill_template, format_website_summary_pairs
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError, NotFoundError
from fastapi import HTTPException, status
import gc
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.chatflow_langchain.service.perplexity.browser_chat.utils import extract_error_message,chat_perplexity_exception_handler
from src.chatflow_langchain.service.config.model_config_openai import DefaultOpenAIModelRepository
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from src.chatflow_langchain.service.perplexity.browser_chat.utils import replace_citations
from src.gateway.exceptions import  ChatPerplexityException
from src.chatflow_langchain.service.perplexity.browser_chat.utils import perplexity_manager
from langchain_core.messages import HumanMessage

llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
openai_llm_apikey_decrypt_service = OpenAILLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
qdrant_vector_store= QdrantVectorStoreService()
prompt_repo = PromptRepository()
file_repo = FileRepository()
      
class PerplexityChatService(AbstractConversationService):
    def initialize_llm(self, api_key_id: str = None, companymodel: str = None,thread_id:str=None,thread_model:str=None,company_id:str=None):
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
            llm_apikey_decrypt_service.initialization(api_key_id, companymodel)
            self.encrypted_key=llm_apikey_decrypt_service.apikey
            self.companyRedis_id=llm_apikey_decrypt_service.companyRedis_id
            default_api_key = DefaultOpenAIModelRepository(company_id=company_id,companymodel=companymodel)
            openai_api_key = default_api_key.get_default_model_key()
            openai_llm_apikey_decrypt_service.initialization(openai_api_key, companymodel)
            self.callback_handler = CustomAsyncIteratorCallbackHandler() 
            # manager_key=perplexity_manager.get_api_key()
            # manager_key_dict={"manager_key":manager_key}
            self.search_context_size='medium'
            self.llm = ChatPerplexity(
                model=llm_apikey_decrypt_service.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature'),
                pplx_api_key=llm_apikey_decrypt_service.decrypt(),
                # pplx_api_key=manager_key_dict.get("manager_key",llm_apikey_decrypt_service.decrypt()),
                streaming=True,
                verbose=False,
                extra_body={'return_images':True,'return_related_questions':True,'web_search_options':{ "search_context_size":  self.search_context_size}}
            )
            self.llm_non_stream = ChatOpenAI(
                model_name=openai_llm_apikey_decrypt_service.model_name,
                temperature=openai_llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=openai_llm_apikey_decrypt_service.decrypt(),
                streaming=True,
                verbose=False
            )
            self.llm_sum_memory = ChatOpenAI(
                model_name=openai_llm_apikey_decrypt_service.model_name,
                temperature=openai_llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=openai_llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "PerplexityChatService.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")

    def initialize_repository(self, chat_session_id: str = None, collection_name: str = None,regenerated_flag:bool=False,thread_id:str=None):
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
                chat_session_id=chat_session_id,
                collection_name=collection_name,
                regenerated_flag=regenerated_flag,
                thread_id=thread_id
            )
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "PerplexityChatService.initialize_repository"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initalize repository: {e}")

    def initialize_memory(self):
        """
        Sets up the memory component using ConversationSummaryBufferMemory.

        Exceptions
        ----------
        Logs an error if the memory initialization fails.
        """
        try:
            self.memory = ConversationSummaryBufferMemory(
                memory_key="chat_history",
                input_key="input",
                llm=self.llm_sum_memory,
                max_token_limit=BrowserChatConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "PerplexityChatService.initialize_memory"}}
            )

   
    
    def prompt_attach(self, additional_prompt_id: str = None, collection_name: str = None):
        """
        Attach additional prompt information to improve the quality and accuracy of the generated content.

        This method initializes and retrieves additional prompt content based on a given prompt ID and collection name.
        The retrieved content is then attached to the main prompt object for further use.

        Parameters
        ----------
        additional_prompt_id : str, optional
            The ID of the additional prompt content to be retrieved and attached. If None, no additional content is attached.
        collection_name : str, optional
            The name of the collection where the prompt content is stored. This is required if `additional_prompt_id` is provided.

        Raises
        ------
        ValueError
            If `additional_prompt_id` is provided but `collection_name` is not.
        Exception
            For any other errors encountered during the initialization or retrieval of the prompt content.
        """
        try:
            if additional_prompt_id:
                if not collection_name:
                    raise ValueError("Collection name must be provided when additional_prompt_id is specified.")

                prompt_repo.initialization(prompt_id=additional_prompt_id, collection_name=collection_name)
                resource_key,resource_value = prompt_repo.get_resource_info()
                if resource_key is not None and resource_value is not None:
                    self.additional_prompt = fill_template(resource_key,resource_value)
                    websites = prompt_repo.get_websites()    
                    summaries = prompt_repo.get_summaries()  
                    formatted_pairs = format_website_summary_pairs(websites,summaries)
                    self.additional_prompt += formatted_pairs
                    logger.info("Successfully attached additional prompt", extra={
                        "tags": {"method": "StreamingDocumentedChatService.prompt_attach"},
                        "additional_prompt_id": additional_prompt_id,
                        "collection_name": collection_name})
                else:
                    self.additional_prompt = None
            else:
                self.additional_prompt = None
        except Exception as e:
            logger.error(
                f"Failed to prompt attach: {e}",
                extra={"tags": {"method": "PerplexityChatService.prompt_attach"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to prompt attach: {e}")

    def create_conversation(self,input_text:str,**kwargs):
        """
        Creates a conversation chain with a custom tag.

        Parameters
        ----------
        tag : str
            A tag to filter the retriever data.

        Exceptions
        ----------
        Logs an error if the conversation creation fails.
        """
        try:
            self.prompt = create_chat_prompt(additional_prompt=self.additional_prompt)
            prompt_list = self.chat_repository_history.messages
            prompt_list.append(HumanMessagePromptTemplate.from_template(template=[
                {"type": "text", "text": '{query}'}]))
            filtered_history = []
            for i, message in enumerate(prompt_list):
                if i > 0 and isinstance(message, HumanMessage) and isinstance(prompt_list[i - 1], HumanMessage):
                    continue  # Skip the first of consecutive HumanMessages
                filtered_history.append(message)
            
            prompt_list = filtered_history
            chat_prompt = ChatPromptTemplate.from_messages(prompt_list)
            if kwargs.get("regenerated_flag"):
                input_text = "Regenerate the above response with improvements in clarity, relevance, and depth as needed. Adjust the level of detail based on the query's requirements—providing a concise response when appropriate and a more detailed, expanded answer when necessary." + input_text
                self.llm.temperature = 1
            self.inputs={"query": input_text}
            self.conversation = LLMChain(llm=self.llm, prompt=chat_prompt)
                
        except Exception as e:
            logger.error(
                f"Failed to create conversation: {e}",
                extra={"tags": {"method": "PerplexityChatService.create_conversation"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create conversation: {e}")
    
    def _get_inputs(self):
        return self.inputs

    async def stream_run_conversation(self, thread_id: str, collection_name: str,regenerated_flag:bool=False,msgCredit:float=None,is_paid_user:bool=False,**kwargs) -> AsyncGenerator[str, None]:
        """
        Executes a conversation and updates the token usage and conversation history.

        thread_id : str
            The thread ID for the conversation.
        collection_name : str
            The collection name for storing conversation history.

        Returns
        -------
        AsyncGenerator[str, None]
            An asynchronous generator yielding response tokens.

        Exceptions
        ----------
        Logs an error if the conversation execution fails.
        """
        try:
            delay_chunk=kwargs.get("delay_chunk",0.0)
            cost = CostCalculator()
            stored_citations = None
            messages = ''
            self.valid_images = None
            async with perplexity_async_cost_handler(model_name=llm_apikey_decrypt_service.model_name,thread_id=thread_id,collection_name=collection_name,search_context_size=self.search_context_size,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as cb,\
            get_mongodb_callback_handler(thread_id=thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=collection_name,regenerated_flag=regenerated_flag,model_name=llm_apikey_decrypt_service.model_name,msgCredit=msgCredit,is_paid_user=is_paid_user,encrypted_key=openai_llm_apikey_decrypt_service.apikey,companyRedis_id=openai_llm_apikey_decrypt_service.companyRedis_id) as mongo_handler:
                async for token in self.conversation.astream_events(self._get_inputs(),{"callbacks":[cb,mongo_handler]},version="v1",stream_usage=True):
                        if token['event']=="on_chat_model_stream":
                            chunk=token['data']['chunk'].content
                            citations = token['data']['chunk'].response_metadata.get('citations')
                            # image_url = token['data']['chunk'].response_metadata.get('images')
                            # if self.valid_images is None:
                            #     valid_images = await filter_valid_images(image_url)
                            #     self.valid_images = valid_images
                            chunk = await replace_citations(chunk,citations,messages)
                            messages+=chunk
                            small_chunk = chunk.encode("utf-8")
                            yield f"data: {small_chunk},citations:{citations}\n\n", 200
                            await asyncio.sleep(delay_chunk)
                        else:
                            pass
                
        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.NotFoundError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai(error_code)

            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
 
        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.RateLimitError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
    
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.LengthFinishReasonError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.ContentFilterFinishReasonError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.APITimeoutError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.APIConnectionError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ChatPerplexityException as e:
            response, status_code = chat_perplexity_exception_handler(e, thread_id, collection_name)
            yield response, status_code

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in OPENAI_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.Exception_Try"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.Exception_Try"}})
                    thread_repo.initialization(thread_id, collection_name)
                    thread_repo.add_message_openai(error_code)
                    content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
                    yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
                except Exception as e:         
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.Exception_Except"}})
                    thread_repo.initialization(thread_id, collection_name)
                    thread_repo.add_message_openai("common_response")
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
                extra={"tags": {"method": "PerplexityChatService.cleanup"}}
            )