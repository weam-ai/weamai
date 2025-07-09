import requests
from bs4 import BeautifulSoup
from src.logger.default_logger import logger
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.output_parsers import JsonOutputParser
import json
from langchain.chains.llm import LLMChain
from fastapi import status, HTTPException
import pandas as pd
import aiohttp
from langchain_google_genai import ChatGoogleGenerativeAI
from src.chatflow_langchain.service.pro_agent.qa_special.utils import attach_status_icon_list,get_user_agents,upload_df_to_s3,scrape_whole_website,extract_data,extract_metrics,extract_json_block
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.tool_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.service.config.model_config_gemini import DefaultGEMINI20FlashModelRepository,GEMINIMODEL
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from src.chatflow_langchain.service.pro_agent.qa_special.config import ChatHistoryConfig, BatchConfig
from src.chatflow_langchain.service.pro_agent.qa_special.chat_prompt_factory import create_chat_prompt,create_chat_prompt_page_speed,create_context_prompt
import asyncio
from langchain_community.callbacks.manager import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback
from src.custom_lib.langchain.tiktoken_load.encoding_cache import get_cached_encoding

from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.callbacks.gemini.cost.context_manager import gemini_sync_cost_handler
from src.chatflow_langchain.repositories.openai_error_messages_config import GENAI_ERROR_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.chatflow_langchain.service.pro_agent.qa_special.utils import extract_google_error_message,extract_google_genai_error_message
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted, GoogleAPICallError
from langchain_google_genai._common import GoogleGenerativeAIError
import os
from src.db.config import get_field_by_name
from src.crypto_hub.utils.crypto_utils import MessageDecryptor
from dotenv import load_dotenv
import pandas as pd
import gc
from langchain_core.exceptions import OutputParserException
from src.chatflow_langchain.service.pro_agent.qa_special.utils import gemini_key_manager
from src.chatflow_langchain.utils.crawler4ai_scrapper import CrawlerService
from src.chatflow_langchain.service.pro_agent.qa_special.utils import split_and_write_text_by_token_limit
from src.celery_worker_hub.web_scraper.tasks.scraping_sitemap import crawler_scraper_task_qa
load_dotenv()
security_key = os.getenv("SECURITY_KEY").encode("utf-8")
decryptor = MessageDecryptor(security_key)

class WebQASpecialService:
    def __init__(self):
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
        self.thread_repo = ThreadRepostiory()
        self.chat_repository_history = CustomAIMongoDBChatMessageHistory()
        self.queues = {
        "checklist": asyncio.Queue(),
        "pagespeed": asyncio.Queue()
    }
        self.processing_complete = {queue_type: False for queue_type in self.queues}
        self.max_chunk_size = 5
        self.enqueue_methods = {
        "checklist": self._enqueue_checklist_items,
        "pagespeed": self._enqueue_pagespeed_items
    }

    async def initilize_chat_input(self,chat_input=None):
        self.chat_input = chat_input
        self.url=self.chat_input.query
        self.company_id=chat_input.company_id
        self.thread_id=chat_input.thread_id
        self.thread_model=chat_input.threadmodel
        self.companymodel=chat_input.companymodel
        self.regenerated_flag=chat_input.isregenerated
        self.delay_chunk=chat_input.delay_chunk
        self.chat_session_id=chat_input.chat_session_id
        self.delay_chunk=chat_input.delay_chunk
        self.isregenerated=chat_input.isregenerated
        self.msgCredit=chat_input.msgCredit
        self.is_paid_user=chat_input.is_paid_user
        self.pro_agent_details = get_field_by_name('setting', 'PRO_AGENT', 'details')
        self.final_flag=False
        self.desktop_pageSpeed_analysis = ''
        self.mobile_pageSpeed_analysis= ''
        self.extract_data = ''
        self.desktop_metrics=''
        self.mobile_metrics=''
        
    async def scrape_url_content(self):
        user_agents = get_user_agents()
        try:
            async with aiohttp.ClientSession() as session:
                for headers in user_agents:
                    async with session.get(self.url, headers=headers, timeout=30) as response:
                        if response.status == 200:
                            text = await response.text()
                            self.source_code = text
                            logger.info(f"Successfully fetched URL: {self.url} with User-Agent: {headers['User-Agent']}")
                            break
                        else:
                            logger.warning(f"Failed to retrieve content from {self.url} with User-Agent: {headers['User-Agent']} and status {response.status}")
                else:
                    raise Exception(f"Failed to retrieve content from {self.url} with all provided User-Agents")
        except Exception as e:
            logger.error(f"Critical error in scrape_url_content: {e}")

    async def scrape_whole_url_content(self):
        response=await scrape_whole_website(self.url)
        self.desktop_task = asyncio.create_task(self.get_pageSpeed_desktop_analysis())
        self.mobile_task = asyncio.create_task(self.get_pageSpeed_mobile_analysis())
        self.source_code = response

    async def crawler_blocked(self):
        response = crawler_scraper_task_qa.apply_async(kwargs={'url': self.url}).get()
        self.desktop_task = asyncio.create_task(self.get_pageSpeed_desktop_analysis())
        self.mobile_task = asyncio.create_task(self.get_pageSpeed_mobile_analysis())
        self.source_code = response
    
    async def get_pageSpeed_desktop_analysis(self):
        try:   
            # PageSpeed_api = self.pro_agent_details.get("qa_specialist").get("pageSpeed")
            # pageSpeedAPIKey = decryptor.decrypt(PageSpeed_api)
            pageSpeedAPIKey=os.environ.get("GOOGLE_PAGE_SPEED")
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                "url": self.url,
                "key": pageSpeedAPIKey,
                "category":["ACCESSIBILITY","BEST_PRACTICES","PERFORMANCE","SEO","PWA"],
            }
            # Check if the request was successful
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=300) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.desktop_checklist_data = {
                            "optimized_images": data['lighthouseResult']['audits']['uses-optimized-images'],
                            "first_meaningful_paint":data['lighthouseResult']['audits']['first-meaningful-paint']
                        }
                        self.desktop_checklist_data = json.dumps(self.desktop_checklist_data)
                        await self.create_pagespeed_batches()
                        self.desktop_pageSpeed_analysis = data
                    else:
                        raise Exception(f"PageSpeed API failed with status: {response.status}")
        except Exception as e:
            logger.error(f"Critical error in PageSpeed Analysis: {e}")

    async def get_pageSpeed_mobile_analysis(self):
        try:   
            PageSpeed_api = self.pro_agent_details.get("qa_specialist").get("pageSpeed")
            pageSpeedAPIKey = decryptor.decrypt(PageSpeed_api)
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                "url": self.url,
                "key": pageSpeedAPIKey,
                "category":["ACCESSIBILITY","BEST_PRACTICES","PERFORMANCE","SEO","PWA"],
                "strategy":'mobile'
            }
            # Check if the request was successful
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, timeout=300) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.mobile_checklist_data = {
                            "optimized_images": data['lighthouseResult']['audits']['uses-optimized-images'],
                            "first_meaningful_paint":data['lighthouseResult']['audits']['first-meaningful-paint']
                        }
                        self.mobile_checklist_data = json.dumps(self.mobile_checklist_data)
                        self.mobile_pageSpeed_analysis = data
                    else:
                        raise Exception(f"PageSpeed API failed with status: {response.status}")
        except Exception as e:
            logger.error(f"Critical error in PageSpeed Analysis: {e}")
    

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
            default_api_key = DefaultGEMINI20FlashModelRepository(company_id=self.company_id,companymodel=self.companymodel).get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(default_api_key, self.companymodel)
            self.model_name =self.llm_apikey_decrypt_service.model_name
            self.bot_data = self.llm_apikey_decrypt_service.bot_data
            self.api_key = self.llm_apikey_decrypt_service.decrypt()
            local_environment = os.getenv("WEAM_ENVIRONMENT", "local")
            # if local_environment in ["prod"]:          
            #     self.api_key=gemini_key_manager.get_api_key()


            self.llm = ChatGoogleGenerativeAI(model= self.llm_apikey_decrypt_service.model_name,
                temperature=0.7,
                disable_streaming=True,
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
                extra={"tags": {"method": "WebQATesterService.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
        

    async def multiple_segementations(self):
        """
        Segments the source code into smaller chunks for processing.

        Returns
        -------
        list
            A list of segmented source code chunks.
        """
        try:
            encoding = get_cached_encoding("gpt2")
            tokens = encoding.encode(self.source_code)
            tokens_count=len(tokens)
            if tokens_count <= BatchConfig.MAX_SOURCE_LIMIT:
                logger.info(f"Source code is within the token limit, no segmentation needed.{tokens_count}")
                pass
            else:
                logger.info(f"Source code exceeds the token limit, segmenting into chunks. Total tokens: {tokens_count}")
                self.chunks = split_and_write_text_by_token_limit(
                    combined_text=self.source_code,
                    token_limit=BatchConfig.BATCH_TOKEN_LIMIT,
                )
                self.source_code=self.chunks[0]
                self.external_sources= ''
                temp_token=0

                try:
                    with gemini_sync_cost_handler(model_name=self.llm_apikey_decrypt_service.model_name) as cb:
                        for i in range(1, len(self.chunks)):
                            self.temp_prompt=create_context_prompt()
                            self.temp_chain = LLMChain(llm=self.llm,prompt=self.temp_prompt)
                            temp_result = await asyncio.to_thread(
                                self.temp_chain.invoke,
                                {'source_code_chunk': self.chunks[i]}
                            )
                            temp_text= temp_result['text']
                            temp_token += len(encoding.encode(temp_text))
                            logger.info(f"Token count for chunk {i}: {temp_token}")

                            if (BatchConfig.BATCH_TOKEN_LIMIT+temp_token) > BatchConfig.MAX_SOURCE_LIMIT:
                                logger.info(f"Token limit exceeded for chunk {i}, stopping segmentation.")
                                break
                            self.external_sources += temp_text + "\n\n"
                        self.thread_repo.initialization(thread_id=self.thread_id, collection_name=self.thread_model)
                        self.thread_repo.update_token_usage(cb)

                    external_context="====external context=======\n\n"
                    self.external_sources = external_context + self.external_sources
                    self.source_code += self.external_sources
                except Exception as e:
                    pass



        except Exception as e:
            logger.error(f"Failed to segment source code: {e}",
                         extra={"tags": {"method": "WebQASpecialService.multiple_segementations"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to segment source code: {e}")
        

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
                regenerated_flag=self.isregenerated,
                thread_id=self.thread_id
            )
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "WebQASpecialService.initialize_repository"}}
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
                extra={"tags": {"method": "WebQATesterService.initialize_memory"}}
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
            self.prompt = create_chat_prompt()
            self.pagespeed_prompt = create_chat_prompt_page_speed()
            self.llm_chain = LLMChain(llm=self.llm,prompt=self.prompt,output_parser=JsonOutputParser())
            self.llm_chain_page_speed = LLMChain(llm=self.llm,prompt=self.pagespeed_prompt,output_parser=JsonOutputParser())
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "WebQASpecialService.create_chain"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create chain: {e}") 
    
    async def create_batches(self):
        try:
            self.df = pd.read_json(BatchConfig.CHECKLIST_PATH)  # Read from a file
            self.category_dict = {category: False for category in self.df['Category'].unique()}
            self.df['id'] = [f'QA_{i:03d}' for i in range(len(self.df))]
            self.checklist_items = []
            for i in range(0, len(self.df), BatchConfig.BATCH_SIZE):
                batches = []
                batch = self.df.iloc[i:i+BatchConfig.BATCH_SIZE]
                for _, row in batch.iterrows(): # Only include rows with non-empty checklist items
                    batches.append({
                        f'{row["id"]}': row["Prompt"],
                        'category':row['Category']
                    })
                self.checklist_items.append(batches)
        except FileNotFoundError:
            logger.error(f"Checklist file not found: {BatchConfig.CHECKLIST_PATH}", exc_info=True)
        except Exception as e:
            logger.error(f"Critical error in create_batches: {e}", exc_info=True)

    async def create_pagespeed_batches(self):
        try:
            self.pageSpeed_df = pd.read_json(BatchConfig.PAGESPEED_PATH)  # Read from a file
            self.pageSpeed_df['id'] = [f'QA_{i:03d}' for i in range(len(self.df), len(self.df) + len(self.pageSpeed_df))]
            self.pagespeed_checklist = []
            for i in range(0, len(self.pageSpeed_df), BatchConfig.BATCH_SIZE):
                batches = []
                batch = self.pageSpeed_df.iloc[i:i+BatchConfig.BATCH_SIZE]
                for _, row in batch.iterrows(): # Only include rows with non-empty checklist items
                    batches.append({
                        f'{row["id"]}': row["Prompt"],
                        'category':row['Category']
                    })
                self.pagespeed_checklist.append(batches)
            
        except FileNotFoundError:
            logger.error(f"Checklist file not found: {BatchConfig.PAGESPEED_PATH}", exc_info=True)
        except Exception as e:
            logger.error(f"Critical error in create_batches: {e}", exc_info=True)

    async def async_initialize_and_update(self, chat_session_id, chat_collection_name, thread_id,cb,queue_type):
        try:
            self.thread_repo.initialization(thread_id=thread_id, collection_name=chat_collection_name)       

            # thread token update
            if queue_type == 'checklist':
                self.thread_repo.overwrite_token_usage(cb)
            else:
                self.thread_repo.update_token_usage(cb)
            
            logger.info("Database successfully stored response",
                extra={"tags":{"method": "WebQASpecialService.async_initialize_and_update"}})
        except Exception as e:
            logger.error(f"Error occurred during async initialization and update: {e}",
                         extra={"tags": {"method": "WebQASpecialService.async_initialize_and_update"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to initialize and update chat thread: {e}")
    async def merge_and_s3_upload(self):
        """
        Asynchronously merges dataframes and prepares the result for S3 upload.
        This function performs the following steps:
        1. Converts the `evaluate_list` attribute to a pandas DataFrame.
        2. Merges the new DataFrame with the existing `df` attribute on the 'id' column, using a right join.
        3. Drops the 'id' and 'Example' columns from the resulting DataFrame.
        4. Reorders the columns of the resulting DataFrame to ['Category', 'Checklist Item', 'status', 'note'].
        Attributes:
            evaluate_list (list): A list of evaluation data to be converted into a DataFrame.
            df (pd.DataFrame): The original DataFrame to be merged with the evaluation data.
            result_df (pd.DataFrame): The resulting DataFrame after merging and processing.
        Returns:
            None
        """
        try:
            mapping_df = pd.DataFrame(self.evaluate_list)
            if hasattr(self, 'pageSpeed_df') and self.pageSpeed_df is not None:
                merge_df = pd.concat([self.df, self.pageSpeed_df])
            else:
                merge_df = self.df
            self.result_df = mapping_df.merge(merge_df, on='id', how='right')
            # self.result_df = self.df.merge(mapping_df, on='id', how='right')
            self.result_df.drop(columns=['id',"Prompt"], inplace=True)
            self.result_df=self.result_df[['Category','Checklist Item','status','note']]
            self.file_url = await upload_df_to_s3(self.result_df,self.extract_data)
            self.file_url = f"\n\n### 🎉 Pipeline Completed Successfully!\n\nYour QA Analysis report is ready.\n\n**[📥 Download QA Report]({self.file_url})**"
            # self.final_ai_message += self.file_url
            if self.desktop_metrics=='' or self.mobile_metrics=='':
                self.chat_repository_history.add_ai_message_kwargs(
                            message=self.final_ai_message,
                            thread_id=self.thread_id,
                            file_url=self.file_url
                            ) 
            else:
                self.chat_repository_history.add_ai_message_kwargs(
                        message=self.final_ai_message,
                        thread_id=self.thread_id,
                        desktop_metrics=self.desktop_metrics,
                        mobile_metrics=self.mobile_metrics,
                        file_url=self.file_url
                        )
        except Exception as e:
            logger.error(f"Critical error in merge_and_s3_upload: {e}",
                        extra={"tags": {"method": "WebQASpecialService.merge_and_s3_upload"}})

    async def _enqueue_checklist_items(self, queue: asyncio.Queue):
        """
        Process checklist items, push each processed chunk into the queue,
        and finally add a sentinel value (None) to signal completion.
        """
        self.evaluate_list=[]
        count=0
        try:
            with gemini_sync_cost_handler(model_name=self.llm_apikey_decrypt_service.model_name) as cb:
                self.final_ai_message=''
                for item in self.checklist_items:
                    try:
                        # Invoke the llm_chain for the current checklist item
                        try:
                            results = await asyncio.to_thread(
                                self.llm_chain.invoke,
                                {
                                    'source_code': self.source_code, 
                                    'checklist_item': item
                                }
                            )
                        except OutputParserException as e:
                            results = {'checklist_item':item,'source_code':self.source_code}
                            results['text'] = extract_json_block(str(e))
                            if results['text'] == None:
                                text_results = []
                                ids_list = [list(i.keys())[0] for i in item]
                                for i in ids_list:
                                    text_results.append({
                                        'id': i,
                                        'status': "empty",
                                        'note': "We were unable to validate the specified checklist due to certain discrepancies. Further review or adjustments may be required."
                                    })

                                # Now update the `results` dictionary with the new structure
                                results.update({
                                    'text': {
                                        'results': text_results
                                    }
                                })
                                logger.info('Raised and handled OuputParserException')
                        # Attach status icons or any additional formatting

                        data,results,self.category_dict = attach_status_icon_list(results,self.category_dict)
                        self.evaluate_list=self.evaluate_list+results

                        self.final_ai_message+=data
                        logger.info(data)
               
                        # Put the processed chunk into the queue
                        update_task = await self.async_initialize_and_update(self.chat_session_id, self.thread_model,self.thread_id, cb, queue_type='checklist')
                        if self.is_paid_user and count < 1:
                            self.thread_repo.update_credits(msgCredit=self.msgCredit)
                            count+=1
                        self.chat_repository_history.add_ai_message(
                            message=self.final_ai_message,
                            thread_id=self.thread_id
                        )
                        self.chat_repository_history.add_message_system(
                            message=self.memory.moving_summary_buffer,
                            thread_id=self.thread_id)
               
                        await queue.put((data, 200))

                    except ResourceExhausted as e:
                        error_content = extract_google_error_message(str(e))
                        logger.error(
                            f"🚨 Google API Error: {error_content}",
                            extra={"tags": {"method": "WebQASpecialService.process_checklist_items.ResourceExhausted"}})
                        self.thread_repo.initialization(self.thread_id, self.thread_model)
                        self.thread_repo.add_message_gemini("resource_exhausted_error")

                        # llm_apikey_decrypt_service.update_deprecated_status(True)
                        content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                        await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))
                    
                    except GoogleAPICallError as e:
                        error_content = extract_google_error_message(str(e))
                        logger.error(
                            f"🚨 Google API Error: {error_content}",
                            extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleAPICallError"}})
                        self.thread_repo.initialization(self.thread_id, self.thread_model)
                        self.thread_repo.add_message_gemini("google_api_call_error")

                        # llm_apikey_decrypt_service.update_deprecated_status(True)
                        content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_call_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                        await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))

                    # Handle GoogleAPIError
                    except GoogleAPIError as e:
                        error_content = extract_google_error_message(str(e))
                        logger.error(
                            f"🚨 Google API Error: {error_content}",
                            extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleAPIError"}})
                        self.thread_repo.initialization(self.thread_id, self.thread_model)
                        self.thread_repo.add_message_gemini("google_api_error")

                        # llm_apikey_decrypt_service.update_deprecated_status(True)
                        content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                        await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))

                    except GoogleGenerativeAIError as e:
                        error_content = extract_google_genai_error_message(str(e))
                        logger.error(
                            f"🚨 Google API Error: {error_content}",
                            extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleGenerativeAIError"}})
                        self.thread_repo.initialization(self.thread_id, self.thread_model)
                        self.thread_repo.add_message_gemini("google_genai_error")

                        # llm_apikey_decrypt_service.update_deprecated_status(True)
                        content = GENAI_ERROR_MESSAGES_CONFIG.get("google_genai_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                        await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))
                    except Exception as e:
                        logger.error(
                            f"🚨 Failed to process checklist items: {str(e)}",
                            extra={"tags": {"method": "WebQASpecialService.process_checklist_items.Exception_Except"}})
                        self.thread_repo.initialization(self.thread_id, self.thread_model)
                        self.thread_repo.add_message_gemini("common_response")
                        content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
                        # yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST
                        await queue.put((json.dumps({
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content
                        }), 400))

                # Signal that processing is complete
                await queue.put((None,200))
        except Exception as e:

            logger.error(
                f"🚨 Failed to  enqueue checklist items: {str(e)}",
                extra={"tags": {"method": "WebQASpecialService._enqueue_checklist_items.Exception"}})
            content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
            await queue.put((json.dumps({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content
            }), 400))

    async def _enqueue_pagespeed_items(self, queue: asyncio.Queue):
        try:

            await self.desktop_task
            await self.mobile_task
            if self.mobile_pageSpeed_analysis=='' or self.desktop_pageSpeed_analysis=='':
                self.final_flag=True
                await queue.put((None, 200))
            else:
                self.extract_data = await extract_data(mobile_data=self.mobile_pageSpeed_analysis,desktop_data=self.desktop_pageSpeed_analysis)
                self.desktop_metrics = await extract_metrics(data=self.desktop_pageSpeed_analysis,device_type='desktop')
                self.mobile_metrics = await extract_metrics(data=self.mobile_pageSpeed_analysis,device_type='mobile')
                with gemini_sync_cost_handler(model_name=self.llm_apikey_decrypt_service.model_name) as cb:
                    for item in self.pagespeed_checklist:
                        try:
                            results = await asyncio.to_thread(
                                self.llm_chain_page_speed.invoke,
                                {
                                    'desktop_page_speed_analysis': self.desktop_checklist_data,
                                    'mobile_page_speed_analysis':self.mobile_checklist_data,
                                    'checklist_item': item
                                }
                            )
                        except OutputParserException as e:
                            results = {'checklist_item':item,'source_code':self.source_code}
                            results['text'] = extract_json_block(str(e))
                            if results['text'] == None:
                                text_results = []
                                ids_list = [list(i.keys())[0] for i in item]
                                for i in ids_list:
                                    text_results.append({
                                        'id': i,
                                        'status': "empty",
                                        'note': "We were unable to validate the specified checklist due to certain discrepancies. Further review or adjustments may be required."
                                    })

                                # Now update the `results` dictionary with the new structure
                                results.update({
                                    'text': {
                                        'results': text_results
                                    }
                                })                        
                                logger.info('Raised and handled OuputParserException')

                        data,results,self.category_dict = attach_status_icon_list(results,self.category_dict)
                        self.evaluate_list += results
                        self.final_ai_message += data
                        await queue.put((data, 200))
                update_task = await self.async_initialize_and_update(self.chat_session_id, self.thread_model,self.thread_id, cb, queue_type='pagespeed') 
                self.final_flag=True

                update_responseModel = {
                    "$set": {
                        "responseModel":GEMINIMODEL.GEMINI_2O_FLASH,
                        "model":self.bot_data
                    }}
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.update_fields(data=update_responseModel)
                # await queue.put((self.file_url, 200))
                await queue.put((None, None))
        except ResourceExhausted as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.ResourceExhausted"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("resource_exhausted_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))
        
        except GoogleAPICallError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleAPICallError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_api_call_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_call_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))

        # Handle GoogleAPIError
        except GoogleAPIError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleAPIError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_api_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))

        except GoogleGenerativeAIError as e:
            error_content = extract_google_genai_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleGenerativeAIError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_genai_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_genai_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            await queue.put((json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED))
        except Exception as e:
            logger.error(
                f"🚨 Failed to process checklist items: {str(e)}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.Exception_Except"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("common_response")
            content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
            # yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST
            await queue.put((json.dumps({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content
            }), 400)) 

    async def process_checklist_items(self):
        """
        Processes each queue in self.queues in sequence. If an exception is raised,
        skip remaining queues and propagate the exception.
        """
        async def _process_queue(queue, queue_type):
            """
            Yields data from the queue until a sentinel (None) is reached or an error occurs.
            """
            while not self.processing_complete[queue_type]:
                try:
                    chunk, status_code = await asyncio.wait_for(queue.get(), timeout=1)
                    if chunk is None:
                        self.processing_complete[queue_type] = True
                        break

                    # If we see a non-200 status_code, yield and break immediately
                    if status_code == 200:
                        for i in range(0, len(chunk), self.max_chunk_size):
                            small_chunk = chunk[i : i + self.max_chunk_size]
                            yield f"data: {small_chunk.encode('utf-8')}\n\n", status_code
                            await asyncio.sleep(self.delay_chunk + 0.03)
                    else:
                        # Once an error chunk is seen, yield it and return
                        yield chunk, status_code
                        return
                # except Exception as e:
                #     logger.info("Error")
                except asyncio.TimeoutError:
                    if queue_type != "checklist":
                        # If we are still waiting for the queue to be populated, send a loader message
                            # This is a placeholder loader message
                        loader = "START_PRO_AGENT_LOADER"
                        yield f"data: {loader.encode('utf-8')}\n\n", 200

        try:
            # Process each queue in order
            for queue_type in self.queues:
                queue = self.queues[queue_type]
                # Enqueue the method that populates the queue
                task = asyncio.create_task(self.enqueue_methods[queue_type](queue))

                # Consume the queue as it's being populated
                async for data in _process_queue(queue, queue_type):
                    yield data
                    # If data is non-200, you can stop processing further
                    if data[1] != 200:
                        # This ensures we stop processing subsequent queues
                        return

                # Wait for the enqueuing task to finish
                await task
            await self.merge_and_s3_upload()

            # If we get here successfully, both queues are processed.
            if self.final_flag:
                json_flag = "JSON_STARTS"
                if self.desktop_metrics=='' or self.mobile_metrics=='':
                    yield f"data: {self.file_url.encode()}\n\n", 200
                else:
                    final_data = {
                        "desktop_metrics": self.desktop_metrics,
                        "mobile_metrics": self.mobile_metrics,
                        "file_url": self.file_url
                    }
                # yield f"data: {json_flag.encode('utf-8')}\n\n", 200
                    yield f"data: {json.dumps(final_data).encode('utf-8')}\n\n", 200

        except HTTPException as he:
            # Re-raise HTTP exceptions verbatim
            raise he

        except ResourceExhausted as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.ResourceExhausted"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("resource_exhausted_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except GoogleAPICallError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleAPICallError"}})
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
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleAPIError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_api_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except GoogleGenerativeAIError as e:
            error_content = extract_google_genai_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.GoogleGenerativeAIError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("google_genai_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_genai_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        except Exception as e:
            logger.error(
                f"🚨 Failed to process checklist items: {str(e)}",
                extra={"tags": {"method": "WebQASpecialService.process_checklist_items.Exception_Except"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_gemini("common_response")
            content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
            # yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST
            yield json.dumps({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content
            }), 400

        finally:
            # Ensure no further data is processed
            self.processing_complete[queue_type] = True
            self.cleanup()

    def cleanup(self):
        """
        Cleans up any resources or state associated with the service.
        """
        cleaned_up = []
        try:
            # List of attributes to clean up
            attributes = [
                'llm',
                'llm_non_stream',
                'memory',
                'queues',
                "desktop_pageSpeed_analysis",
                "mobile_pageSpeed_analysis",
                'llm_chain',
                'llm_chain_page_speed',
                "desktop_metrics",
                "mobile_metrics",
                "evaluate_list",
                "merge_df",
                "mapping_df",
                "result_df",
                "df",
                "pageSpeed_df",
                "pagespeed_checklist",
                "checklist_items",
                "llm_sum_memory",
                "desktop_checklist_data",
                "mobile_checklist_data",
                "crawler_service"
            ]

            for attr in attributes:
                if hasattr(self, attr):
                    # Deletes the attribute from the instance
                    delattr(self, attr)
                    # Adds the attribute name to the cleaned_up list
                    cleaned_up.append(attr)

            gc.collect()  # Force garbage collection to free memory

            # Log a single message with the list of cleaned-up attributes
            if cleaned_up:
                logger.info(
                    f"Successfully cleaned up resources: {', '.join(cleaned_up)}."
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "QA_Agent.cleanup"}}
            )