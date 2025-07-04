from concurrent.futures import thread
from httpx import delete
from openai import audio
from src.logger.default_logger import logger
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains.llm import LLMChain
from fastapi import status, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.tool_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.service.pro_agent.sales_call_analyzer.config import ChatHistoryConfig
from src.chatflow_langchain.service.pro_agent.sales_call_analyzer.chat_prompt_factory import create_chat_prompt,create_chat_prompt_with_url
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
import os
from src.db.config import get_field_by_name
from src.crypto_hub.utils.crypto_utils import crypto_service
from dotenv import load_dotenv
import pandas as pd
from src.chatflow_langchain.service.config.model_config_gemini import DefaultGEMINI20FlashModelRepository,GEMINIMODEL
from google import genai
from src.celery_service.upload_file.audio import upload_gemini_audio
import requests
from src.chatflow_langchain.utils.crawler4ai_scrapper import CrawlerService
import asyncio
from src.custom_lib.langchain.callbacks.gemini.cost.context_manager import gemini_async_cost_handler
from src.custom_lib.langchain.callbacks.gemini.mongodb.context_manager import get_mongodb_callback_handler
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted, GoogleAPICallError
import json
from src.chatflow_langchain.service.gemini.doc.utils import extract_google_error_message,extract_google_genai_error_message
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG, GENAI_ERROR_MESSAGES_CONFIG
from langchain_google_genai._common import GoogleGenerativeAIError
from src.celery_worker_hub.extraction.tasks import extract_text_task
from src.custom_lib.langchain.callbacks.gemini.cost.cost_calc_handler import _get_gemini_claude_token_cost
from src.celery_worker_hub.extraction.utils import map_file_url,validate_file_url
from playwright.async_api import Page
from src.gateway.utils import delete_file_from_s3
from bs4 import BeautifulSoup
import gc
from src.chatflow_langchain.service.pro_agent.qa_special.utils import URLCheckerService
from src.chatflow_langchain.service.pro_agent.sales_call_analyzer.utils import launch_and_prepare_page
from src.celery_worker_hub.web_scraper.tasks.scraping_sitemap import crawler_scraper_task_sales
# Define the API endpoint and the payload
load_dotenv()

class SalesFathomService:
    def __init__(self):
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
        self.thread_repo = ThreadRepostiory()
        self.chat_repository_history = CustomAIMongoDBChatMessageHistory()

    def get_size(self, num_bytes):
        gb = num_bytes / (1024 ** 3)
        return gb


    async def initilize_chat_input(self,chat_input=None):
        self.chat_input = chat_input
        self.company_id=chat_input.company_id
        self.FathomUrl=self.chat_input.query
        self.thread_id=chat_input.thread_id
        self.thread_model=chat_input.threadmodel
        self.companymodel=chat_input.companymodel
        self.regenerated_flag=chat_input.isregenerated
        self.delay_chunk=chat_input.delay_chunk
        self.chat_session_id=chat_input.chat_session_id
        self.msgCredit=chat_input.msgCredit
        self.is_paid_user=chat_input.is_paid_user
        self.agent_info = chat_input.agent_extra_info
        self.pro_agent_details = get_field_by_name('setting', 'PRO_AGENT', 'details')
        self.product_summary_code = chat_input.product_summary_code
        self.url =  self.agent_info.get("url","")
    
    async def initialize_llm(self):
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
            default_api_key = DefaultGEMINI20FlashModelRepository(company_id=self.company_id,companymodel=self.companymodel)
            self.encrypted_key = default_api_key.get_encrypt_key()
            default_api_key = default_api_key.get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(default_api_key, self.companymodel)
            self.bot_data = self.llm_apikey_decrypt_service.bot_data
            self.model_name =self.llm_apikey_decrypt_service.model_name
            self.api_key = self.llm_apikey_decrypt_service.decrypt()
            local_environment = os.getenv("WEAM_ENVIRONMENT", "local")
            if local_environment in ["prod"]:          
                Qa_specialist_api = self.pro_agent_details.get("qa_specialist").get("gemini")
                self.encrypted_key = Qa_specialist_api
                self.api_key = crypto_service.decrypt(Qa_specialist_api)

            self.llm = ChatGoogleGenerativeAI(model= self.llm_apikey_decrypt_service.model_name,
                temperature=1,
                disable_streaming=False,
                verbose=False,
                api_key=self.api_key)
        
            self.llm_non_stream = ChatGoogleGenerativeAI(model= self.llm_apikey_decrypt_service.model_name,
                temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                disable_streaming=True,
                verbose=False,
                api_key=self.api_key)
                
            self.llm_sum_memory = ChatGoogleGenerativeAI(model= self.llm_apikey_decrypt_service.model_name,
                temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                disable_streaming=True,
                verbose=False,
                api_key=self.api_key)
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "SalesFathomService.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
        
    async def extract_transcript_from_page(self, page: Page) -> str:
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        entries = soup.find_all(['figcaption', 'blockquote'])

        output = []
        current_speaker = ""
        current_text = ""

        for entry in entries:
            text = entry.get_text(strip=True)
            if entry.name == 'figcaption':
                if current_text:
                    output.append(f"{current_speaker}: {current_text.strip()}")
                current_speaker = text
                current_text = ""
            elif entry.name == 'blockquote':
                current_text += f" {text}" if current_text else text

        if current_text:
            output.append(f"{current_speaker}: {current_text.strip()}")

        return "\n\n".join(output)

    async def get_fathom_transcript_with_playwright(self,url: str,scroll: bool = True,scroll_delay: float = 2.0,page_timeout: int = 60000,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36") -> str:
        browser = None
        playwright = None
        context = None
        page = None
        try:
            playwright, browser, page, context = await launch_and_prepare_page(url=url,user_agent=user_agent,page_timeout=page_timeout,scroll=scroll,scroll_delay=scroll_delay)
            transcript = await self.extract_transcript_from_page(page)
            logger.info("Transcript extraction complete.")
            return transcript

        except Exception as e:
            logger.error(f"Error scraping Fathom URL: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch transcript")
        finally:
             try:
                 if page:
                     await page.close()
                 if context:
                     await context.close()
                 if browser:
                     await browser.close()
                 if playwright:
                     await playwright.stop()
             except Exception as e:
                 logger.warning(f"[Cleanup Failed] Could not close browser resources: {e}")
    
    async def fetch_transcript_and_summary(self):
        try:

            self.transcript = await self.get_fathom_transcript_with_playwright(url=self.FathomUrl)
            # Check the response
            if self.product_summary_code == "URL":
                checker = URLCheckerService(self.url)
                reachable, not_reachable = await checker.check_urls_async()
                if not reachable:
                    logger.error(f"No reachable URLs found from provided input: {self.url}")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Unable to reach the URL: {self.url}. Please check if the URL is correct and try again.")
                self.scraped_content = crawler_scraper_task_sales.apply_async(kwargs={'url': reachable[0]}).get()

            else:
                self.file_url = map_file_url(self.url, 's3_url')
                self.scraped_content = extract_text_task(file_url=self.file_url,file_type='txt',source='s3_url',page_wise="False")
                self.url = self.url.split('/', 1)[1] 
                delete_file_from_s3(s3_bucket=self.bucket_name,file_key=self.url)
                logger.info(f"File Successfully deleted from s3 {self.url}")
        except Exception as e:
            logger.error(f"An unexpected error occurred in fetch_transcript_and_summary: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="An internal error occurred during fetch transcript and summary")


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
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "SalesFathomService.initialize_repository"}}
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
                input_key="question",
                output_key="answer",
                llm=self.llm_sum_memory,
                max_token_limit=ChatHistoryConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "SalesFathomService.initialize_memory"}}
            )
            
    async def create_chain(self):
        """
        Creates the prompt for the LLM using the scraped content.

        Returns
        -------
        str
            The prompt for the LLM.
        """
        try:

            if self.product_summary_code == "URL":
                self.prompt = create_chat_prompt_with_url(self.agent_info.get('prompt',None))
                self.llm_chain = LLMChain(llm=self.llm,prompt=self.prompt)
                self.inputs = {'transcript': self.transcript, 'scraped_content': self.scraped_content,'url':self.url}
            else:
                self.prompt = create_chat_prompt(self.agent_info.get('prompt',None))
                self.llm_chain = LLMChain(llm=self.llm,prompt=self.prompt)
                self.inputs = {'transcript': self.transcript, 'scraped_content': self.scraped_content}
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "SalesFathomService.create_chain"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create chain: {e}") 
        
    async def run_chain(self,kwargs={}):
            try:

                async with gemini_async_cost_handler(model_name=self.llm_apikey_decrypt_service.model_name,thread_id=self.thread_id,collection_name=self.thread_model) as cb,\
                get_mongodb_callback_handler(thread_id=self.thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=self.thread_model,model_name=self.llm_apikey_decrypt_service.model_name,regenerated_flag=self.regenerated_flag,msgCredit=self.msgCredit,is_paid_user=self.is_paid_user,audio_context=self.transcript) as mongo_handler:
                        async for token in self.llm_chain.astream_events(self.inputs,{"callbacks":[cb,mongo_handler]},version="v1",stream_usage=True):
                            if token['event']=="on_chat_model_stream":
                                max_chunk_size = 5  # Set your desired chunk size
                                chunk=token['data']['chunk'].content
                                for i in range(0, len(chunk), max_chunk_size):
                                    small_chunk = chunk[i:i + max_chunk_size]
                                    small_chunk = small_chunk.encode("utf-8")
                                    yield f"data: {small_chunk}\n\n", 200
                                    await asyncio.sleep((self.delay_chunk))
                update_responseModel = {
                    "$set": {
                        "responseModel":GEMINIMODEL.GEMINI_2O_FLASH,
                        "model":self.bot_data
                    }}
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.update_fields(data=update_responseModel)
            except ResourceExhausted as e:
                error_content = extract_google_error_message(str(e))
                logger.error(
                    f"🚨 Google API Error: {error_content}",
                    extra={"tags": {"method": "SalesFathomService.run_chain.ResourceExhausted"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_gemini("resource_exhausted_error")

                # llm_apikey_decrypt_service.update_deprecated_status(True)
                content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
            
            except GoogleAPICallError as e:
                error_content = extract_google_error_message(str(e))
                logger.error(
                    f"🚨 Google API Error: {error_content}",
                    extra={"tags": {"method": "SalesFathomService.run_chain.GoogleAPICallError"}})
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
                    extra={"tags": {"method": "SalesFathomService.run_chain.GoogleAPIError"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_gemini("google_api_error")

                # llm_apikey_decrypt_service.update_deprecated_status(True)
                content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

            except GoogleGenerativeAIError as e:
                error_content = extract_google_genai_error_message(str(e))
                logger.error(
                    f"🚨 Google API Error: {error_content}",
                    extra={"tags": {"method": "SalesFathomService.run_chain.GoogleGenerativeAIError"}})
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
                            extra={"tags": {"method": "SalesFathomService.Exception.extract_google_error_message"}})

                    # If no content from the first extractor, try the second one
                    if not error_content:
                        try:
                            error_content = extract_google_genai_error_message(str(e))
                        except Exception as inner_e:
                            logger.warning(
                                f"Warning: Failed to extract using extract_google_genai_error_message: {inner_e}",
                                extra={"tags": {"method": "SalesFathomService.Exception.extract_google_genai_error_message"}})

                    # Default error message if extraction fails
                    if not error_content:
                        error_content = DEV_MESSAGES_CONFIG.get("genai_message")

                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_content}",
                        extra={"tags": {"method": "SalesFathomService.run_chain.Exception_Try"}})
                    self.thread_repo.initialization(self.thread_id, self.thread_model)
                    self.thread_repo.add_message_gemini("common_response")
                    content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                    yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  

                except Exception as inner_e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {inner_e}",
                        extra={"tags": {"method": "SalesFathomService.run_chain.Exception_Except"}})
                    self.thread_repo.initialization(self.thread_id, self.thread_model)
                    self.thread_repo.add_message_gemini("common_response")
                    content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
                    yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST
            finally:
                self.cleanup()

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
                'FathomUrl',
                'llm_chain',
                'inputs',
                'transcript',
                'chat_repository_history',
                'scraped_content',
                'agent_info',
                'vector_store_api_decrypt_service',
                'llm_apikey_decrypt_service',
                'cost_calculator',
                'crawler'  # Add this if it's used in the service
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
                extra={"tags": {"method": "SalesAudioService.cleanup"}}
            )