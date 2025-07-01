import openai
import os
from langchain_openai import ChatOpenAI
from fastapi import HTTPException, status
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains.llm import LLMChain
import aiohttp
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse
import pyhtml2md
from langchain_community.callbacks.manager import get_openai_callback
from bson.objectid import ObjectId
from src.logger.default_logger import logger
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.tool_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.seo_summaries import SeoRepo
from src.chatflow_langchain.service.pro_agent.config.model_config import DocConfig
from src.chatflow_langchain.service.pro_agent.seo_optimizer.chat_prompt_factory import create_prompt_summary,create_prompt_audience
from src.chatflow_langchain.utils.user_agents import get_user_agents
from src.chatflow_langchain.service.pro_agent.seo_optimizer.sitemap_crawler import SitemapTitleScraper
from src.celery_worker_hub.web_scraper.tasks.scraping_sitemap import scrape_sitemap_task
from src.chatflow_langchain.service.config.model_config_openai import OPENAIMODEL,DefaultGPT4oMiniModelRepository
import asyncio
from src.chatflow_langchain.utils.crawler4ai_scrapper import CrawlerService

class BusinessSummaryGenerator:
    def __init__(self,current_user_data):
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
        self.thread_repo = SeoRepo()
        self.chat_repository_history = CustomAIMongoDBChatMessageHistory()
        self.current_user_data=current_user_data
        self.crawler_service = CrawlerService()

    async def initialize_chat_input(self,chat_input):

  
        self.chat_input = chat_input
        self.company_id=chat_input.company_id
        self.thread_id=str(ObjectId())
        self.user_id=str(self.current_user_data["_id"])
        self.thread_model=chat_input.threadmodel
        self.companymodel=chat_input.companymodel
        self.brain_id=str(ObjectId())
        self.regenerated_flag=chat_input.isregenerated
        self.chat_session_id=str(ObjectId())
        self.isregenerated=chat_input.isregenerated
        self.msgCredit=chat_input.msgCredit
        self.is_paid_user=chat_input.is_paid_user
        self.agent_extra_info=chat_input.agent_extra_info
        self.project_name=self.agent_extra_info.get("project_name","Unnamed Project")
        self.website_url=self.agent_extra_info.get("website_url","Not Specified")
        self.location=self.agent_extra_info.get("location","Not Specified")
        self.target_keywords=self.agent_extra_info.get("target_keywords","Not Specified")
        self.industry=self.agent_extra_info.get("industry"," ")
        self.business_summary=self.agent_extra_info.get("business_summary"," ")
        self.target_audience=self.agent_extra_info.get("target_audience"," ")
        self.language=self.agent_extra_info.get("language",[])
        # Run the sitemap title scraper as a background task
        data={"website":self.website_url,"thread_id":self.thread_id,"company_id":self.company_id,"chat_session_id":self.chat_session_id,"brain_id":self.brain_id}
 
        task = scrape_sitemap_task.delay(data=data) 

       
    
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
            self.api_key_id=DefaultGPT4oMiniModelRepository(self.company_id,self.companymodel).get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(self.api_key_id, self.companymodel)
            self.model_name = OPENAIMODEL.MODEL_VERSIONS[self.llm_apikey_decrypt_service.model_name]
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.7,
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False,
                stream_usage=True
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
        
    async def scrape_url_content(self):
        try:
            logger.info(f"🌐 Starting crawl for: {self.website_url}")
            result = await self.crawler_service.crawl_and_clean_non_markdown(self.website_url)

            # title = getattr(result, "title", "No Title Found")
            # description = getattr(result, "description", "No meta description found")
            metadata = getattr(result, "metadata", {})
            title = metadata.get("title", "No Title Found")
            description = metadata.get("description", "No meta description found")
            content = (
                f"Source: {self.website_url}\n"
                f"Title: {title}\n"
                f"Meta Description: {description}\n"
                f"Meta Tags:\n"
            )
            for key, value in metadata.items():
                content += f"{key}: {value}\n"

            content += f"\nMarkdown Content:\n{result.markdown}\n"

            self.website_content = content
            logger.info(f"✅ Successfully crawled and parsed {self.website_url}")

        except HTTPException as he:
            logger.warning(f"⚠️ HTTP error while crawling {self.website_url}: {he.detail}")
            raise
        except Exception as e:
            logger.error(f"🔥 Critical error in scrape_url_content: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during scraping")

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

        self.audience_prompt = create_prompt_audience()
        self.summary_prompt = create_prompt_summary()
   
    async def create_chain(self):
        """Run the LLM chain to generate content using OpenAI API."""
        try:
            self.summary_chain=LLMChain(
                llm=self.llm,
                prompt= self.summary_prompt)
            self.audience_chain=LLMChain(
                llm=self.llm,
                prompt= self.audience_prompt)
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
       
    async def run_chain(self):
        """Generate both business summary and target audience analysis.""" 
        try:
            with get_openai_callback() as cb: 
                # Convert location to string if it's a list
                if isinstance(self.location, list):
                    self.location_str = ', '.join(self.location)
                
                self.business_summary = await self.summary_chain.ainvoke({
                                        'project_name': self.project_name, 
                                        'location': self.location_str,
                                        'website_url': self.website_url,
                                        'website_content': self.website_content,
                                
                                    })
                self.business_summary=self.remove_newlines(self.business_summary['text'])
                
        
                self.target_audience = await self.audience_chain.ainvoke({'project_name': self.project_name, 'location': self.location_str,'target_keywords': self.target_keywords, 'industry': self.industry})
                self.target_audience=self.target_audience['text']
            self.cb=cb


            await asyncio.to_thread(self.perform_thread_operations)
            
            # record_id = db_manager.insert_record(self.summary, self.target_audience)
            return JSONResponse(
                content={
                "status": 200,
                "message": "Your request has been processed successfully.",
                "data": {
    
                    "business_summary":  self.business_summary,
                    "target_audience": self.target_audience
                }
                },
                status_code=status.HTTP_200_OK)
        
        except HTTPException as e:
            raise e  # Reraise HTTPExceptions to be handled by FastAPI

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate business summary and target audience: {str(e)}")
        

    def perform_thread_operations(self):
        self.summary_data = {
            "$set": {
                "proAgentData.step1": {
                    "business_summary": self.business_summary,
                    "target_audience": self.target_audience,
                    "target_keywords": self.target_keywords,
                    "language": self.language,
                    "location": self.location
                },
                "userId": ObjectId(self.user_id),
                "companyId": ObjectId(self.company_id)
            }
        }

        self.thread_repo.initialization_thread_id(self.thread_id, collection_name=self.thread_model)
        self.thread_repo.update_fields_insert(data=self.summary_data)
        self.thread_repo.update_token_usage(cb=self.cb)

    async def insert_defulat_summary(self):
        self.thread_repo.initialization_thread_id(self.thread_id, collection_name=self.thread_model)
        self.summary_data={"$set":{"proAgentData.step1":{"business_summary":self.business_summary,"target_audience":self.target_audience,\
                                                            "target_keywords":self.target_keywords,"language":self.language,"location":self.location}, "userId":ObjectId(self.user_id),"companyId":ObjectId(self.company_id)}}
        self.thread_repo.update_fields_insert(data=self.summary_data)
            
    def remove_newlines(self, input_string: str) -> str:
        """
        Removes newline characters from the given string.

        Parameters
        ----------
        input_string : str
            The string from which to remove newline characters.

        Returns
        -------
        str
            The string with newline characters removed.
        """
        return input_string.replace('\n', '')