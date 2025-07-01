from typing import List, Optional
import openai
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from fastapi import HTTPException, status
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains.llm import LLMChain
import gc
import os
import json
import asyncio
from google import genai
from google.genai import types
from src.logger.default_logger import logger
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.tool_history import CustomAIMongoDBChatMessageHistory
from src.prompts.langchain.pro_agent.video_analyzer.video_analyzer_prompt import context_prompt, system_prompt
from src.chatflow_langchain.service.pro_agent.config.model_config import DocConfig
from src.chatflow_langchain.service.pro_agent.video_analysis.chat_prompt_factory import create_chat_prompt,create_context_prompt
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from langchain_core.messages import HumanMessage
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.gemini.mongodb.context_manager import get_mongodb_callback_handler
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.chatflow_langchain.service.pro_agent.video_analysis.utils import get_cached_token_cost
from src.chatflow_langchain.service.config.model_config_gemini import DefaultGEMINI20FlashModelRepository,GEMINIMODEL
from src.crypto_hub.utils.crypto_utils import MessageDecryptor
from src.chatflow_langchain.service.pro_agent.video_analysis.config import VideoModel
from src.custom_lib.langchain.callbacks.gemini.cost.context_manager import gemini_async_cost_handler,gemini_sync_cost_handler

from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG, GENAI_ERROR_MESSAGES_CONFIG
from src.chatflow_langchain.service.gemini.doc.utils import extract_google_error_message,extract_google_genai_error_message
from langchain_google_genai._common import GoogleGenerativeAIError
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted, GoogleAPICallError
from langchain_google_genai import ChatGoogleGenerativeAI
from src.db.config import get_field_by_name

security_key = os.getenv("SECURITY_KEY").encode("utf-8")
decryptor = MessageDecryptor(security_key)

class VideoChatService:
    def __init__(self):
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
        self.thread_repo = ThreadRepostiory()
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
        self.file=self.agent_extra_info.get("file","")
        self.chat_session_id=self.chat_input.chat_session_id
        self.user_query=self.agent_extra_info.get("user_prompt","")
        self.file_collection = "file"
        self.pro_agent_details = get_field_by_name('setting', 'PRO_AGENT', 'details')
        self.delay_chunk=chat_input.delay_chunk

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
            default_api_key = DefaultGEMINI20FlashModelRepository(company_id=self.company_id,companymodel=self.companymodel).get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(default_api_key, self.companymodel)
            self.model_name =self.llm_apikey_decrypt_service.model_name
            self.api_key = self.llm_apikey_decrypt_service.decrypt()
           
            local_environment = os.getenv("WEAM_ENVIRONMENT", "local")
            if local_environment in ["prod"]:          
                Qa_specialist_api = self.pro_agent_details.get("qa_specialist").get("gemini")
                self.api_key = decryptor.decrypt(Qa_specialist_api)

            self.client=genai.Client(api_key=self.api_key)
            self.file_metadata = self.client.files.get(name=self.file)
            
            self.llm_sum_memory = ChatGoogleGenerativeAI(model= self.llm_apikey_decrypt_service.model_name,
                temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                disable_streaming=True,
                verbose=False,
                api_key=self.api_key)

 
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "VideoChatService.initialize_llm"}}
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
                extra={"tags": {"method": "VideoChatService.initialize_repository"}}
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
                extra={"tags": {"method": "VideoChatService.initialize_memory"}}
            )
    
    async def sync_phase(self):
        try:
            with gemini_sync_cost_handler(model_name=VideoModel.chat_model) as cb:
                    logger.info(
                        "Started sync call",
                        extra={"tags": {"method": "VideoChatService.sync_phase"}}
                    )
                    self.cache = await asyncio.to_thread(
                                self.client.caches.create,
                                model=VideoModel.model,
                                config=types.CreateCachedContentConfig(
                                    display_name='Cached Content',
                                    system_instruction=system_prompt,
                                    contents=[self.file_metadata],
                                    ttl="300s",
                                
                                )
                     )

            

                    self.llm = ChatGoogleGenerativeAI(model= self.llm_apikey_decrypt_service.model_name,
                        temperature=0.7,
                        disable_streaming=False,
                        cached_content=self.cache.name,
                        verbose=False,
                        api_key=self.api_key)
                
                    self.llm_non_stream = ChatGoogleGenerativeAI(model= self.llm_apikey_decrypt_service.model_name,
                        temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                        disable_streaming=True,
                        cached_content=self.cache.name,
                        verbose=False,
                        api_key=self.api_key)
                    
                    self.video_context=await self.llm_non_stream.ainvoke([HumanMessage(context_prompt)])
                    self.video_context = self.video_context.content
                    self.thread_repo.initialization(self.thread_id,self.thread_model)
                    self.thread_repo.update_token_usage(cb=cb)
                    self.thread_repo.update_cache_token_usage(get_cached_token_cost(self.cache.usage_metadata.total_token_count))
                    
                    logger.info(
                        "Sync call ended successfully.",
                        extra={"tags": {"method": "VideoChatService.sync_phase"}}
                    )
                    await self.queue.put((self.video_context,200))
                   
        except Exception as e:



            logger.exception("Error occurred during sync_phase")
            fallback_value = "Error: Could not generate video context"
            logger.error(
                f"🚨 Failed to process checklist items: {str(e)}",
                extra={"tags": {"method": "VideoChatService.sync_phase.Exception_Except"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("agent_error")
            content = GENAI_ERROR_MESSAGES_CONFIG.get("agent_error")
            # yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST
            error=(json.dumps({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content
            }), 400)

            await self.queue.put(error)

    async def run_chain(self,kwargs={}):
        try:
            self.queue=asyncio.Queue()
            task=asyncio.create_task(self.sync_phase())
            while True:
                try:
                    # wait up to 0.5s for a result
                    video_context,status_code = await asyncio.wait_for(self.queue.get(), timeout=1)


                    if status_code!=200:
                        content = GENAI_ERROR_MESSAGES_CONFIG.get("agent_error")['content']
                        yield f"data: {content.encode('utf-8')}\n\n", 200
                        task.cancel()  # Cancel the sync_phase task if failed
                        return 
                    else:
                        break  # got it! break out of loader loop
                except asyncio.TimeoutError:
                    # nothing yet—stream the loader
                   loader = "LOOM_VIDEO_LOADER"
                   yield f"data: {loader.encode('utf-8')}\n\n", 200
                   await asyncio.sleep(0.3)

           
           
            await task
            async with gemini_async_cost_handler(model_name=self.llm_apikey_decrypt_service.model_name,thread_id=self.thread_id,collection_name=self.thread_model,cache_tokens=self.cache.usage_metadata.total_token_count) as cb,\
            get_mongodb_callback_handler(thread_id=self.thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=self.thread_model,model_name=self.llm_apikey_decrypt_service.model_name,regenerated_flag=self.regenerated_flag,msgCredit=self.msgCredit,is_paid_user=self.is_paid_user,video_context=video_context) as mongo_handler:
    
                async for token in self.llm.astream_events([HumanMessage(self.user_query)],{"callbacks":[cb,mongo_handler]},version="v1"):
           
                    if token['event']=="on_chat_model_stream":
                        max_chunk_size = 5  # Set your desired chunk size
                        chunk=token['data']['chunk'].content
                        for i in range(0, len(chunk), max_chunk_size):
                            small_chunk = chunk[i:i + max_chunk_size]
                            small_chunk = small_chunk.encode("utf-8")
                            yield f"data: {small_chunk}\n\n", 200
                            await asyncio.sleep((self.delay_chunk))
                    else:
                        pass
            

      # Handle ResourceExhaustedError
        except ResourceExhausted as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "VideoChatService.stream_run_conversation.ResourceExhausted"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("resource_exhausted_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except GoogleAPICallError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "VideoChatService.stream_run_conversation.GoogleAPICallError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_api_call_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_call_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        # Handle GoogleAPIError
        except GoogleAPIError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "VideoChatService.stream_run_conversation.GoogleAPIError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_api_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except GoogleGenerativeAIError as e:
            error_content = extract_google_genai_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "VideoChatService.stream_run_conversation.GoogleGenerativeAIError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_genai_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_genai_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except Exception as e:
            try:
                # Attempt to extract the error message using both extractors
                error_content = None

                # First, try extracting with extract_google_error_message
                try:
                    error_content = extract_google_error_message(str(e))
                except Exception as inner_e:
                    logger.warning(
                        f"Warning: Failed to extract using extract_google_error_message: {inner_e}",
                        extra={"tags": {"method": "VideoChatService.Exception.extract_google_error_message"}})

                # If no content from the first extractor, try the second one
                if not error_content:
                    try:
                        error_content = extract_google_genai_error_message(str(e))
                    except Exception as inner_e:
                        logger.warning(
                            f"Warning: Failed to extract using extract_google_genai_error_message: {inner_e}",
                            extra={"tags": {"method": "VideoChatService.Exception.extract_google_genai_error_message"}})

                # Default error message if extraction fails
                if not error_content:
                    error_content = DEV_MESSAGES_CONFIG.get("genai_message")

                logger.error(
                    f"🚨 Failed to stream run conversation: {error_content}",
                    extra={"tags": {"method": "VideoChatService.stream_run_conversation.Exception_Try"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  

            except Exception as inner_e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {inner_e}",
                    extra={"tags": {"method": "VideoChatService.stream_run_conversation.Exception_Except"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST

        finally:
            # Ensure cleanup is always called
            self.client.files.delete(name=self.file)
            if hasattr(self, "cache"):
                self.client.caches.delete(name=self.cache.name)
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

