import asyncio
import json
from langchain.memory import ConversationSummaryBufferMemory
from bson.objectid import ObjectId
from typing import AsyncGenerator
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from src.logger.default_logger import logger
from src.chat.service.base.abstract_conversation_service import AbstractConversationService
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.langchain_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.chatflow_langchain.service.gemini.custom_gpt.simple_chat.chat_prompt_factory import UserCustomGPTPrompt
from src.chatflow_langchain.repositories.custom_gpt_repository import CustomGPTRepository
from src.crypto_hub.services.gemini.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.gemini.cost.context_manager import gemini_async_cost_handler, gemini_sync_cost_handler
from src.custom_lib.langchain.callbacks.gemini.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.gemini.streaming.context_manager import async_streaming_handler
from src.custom_lib.langchain.chain.custom_conversation_chain import CustomConversationChain
from fastapi import HTTPException, status
from src.chatflow_langchain.service.gemini.custom_gpt.config import CustomGptChatConfig,GetLLMkey
from src.chatflow_langchain.utils.fill_additional_prompt import fill_template, format_website_summary_pairs
import gc
from src.chatflow_langchain.repositories.openai_error_messages_config import GENAI_ERROR_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.chatflow_langchain.service.gemini.custom_gpt.simple_chat.utils import extract_google_genai_error_message,extract_google_error_message
from src.celery_worker_hub.web_scraper.tasks.scraping_sitemap import crawler_scraper_task
from langchain_core.tools import tool
from langchain.chains import LLMChain
from langchain_core.messages import SystemMessage, HumanMessage
from src.chatflow_langchain.service.config.model_config_gemini import GEMINIMODEL,Functionality
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted, GoogleAPICallError
from langchain_google_genai._common import GoogleGenerativeAIError
import re
from src.chatflow_langchain.service.gemini.config.gemini_tool_description import ToolServiceDescription
from src.round_robin.llm_key_manager import APIKeyUsageService

llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
prompt_repo = PromptRepository()
custom_gpt_repo = CustomGPTRepository()
user_custom_prompt = UserCustomGPTPrompt()

class GeminiCustomGPTStreamingSimpleChatServiceTool(AbstractConversationService):
    def Initilization_custom_gpt(self,custom_gpt_id:str=None,customgptmodel:str=None):
        """
        Initializes the Custom GPT with the specified API key and company model.

        Parameters
        ----------
        custom_gpt_id : str, optional
            The API key ID used for decryption and initialization.
        customgptmodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:
        
            custom_gpt_repo.initialization(custom_gpt_id=custom_gpt_id, collection_name=customgptmodel)
            
        except Exception as e:
            logger.error(
                f"Failed to initialize custom gpt: {e}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.Initilization_custom_gpt"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize custom gpt: {e}")
        
  
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
            self.chat_repository_history = CustomAIMongoDBChatMessageHistory()
            self.chat_repository_history.initialize(
                chat_session_id=chat_session_id,
                collection_name=collection_name,
                thread_id=thread_id,
                regenerated_flag=regenerated_flag
            )
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.initialize_repository"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initalize repository: {e}")

    def initialize_llm(self, company_id:str=None,companymodel: str = None,**kwargs):
        """
        Initializes the LLM with the specified API key and company model.

        Parameters
        ----------
        companymodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:
            self.api_usage_service = APIKeyUsageService()
            if kwargs.get("regenerated_flag"):
                self.api_key_id=kwargs.get('llm_apikey')
            else:
                self.api_key_id=custom_gpt_repo.get_gpt_llm_key_id()
            if self.api_key_id is None:
                get_key=GetLLMkey()
                self.query = {
                    "name": GEMINIMODEL.DEFAULT_TOOL_MODEL,
                    "company.id": ObjectId(company_id)
                    }
                self.projection = {
                        '_id': 1
                    }
                self.api_key_id = get_key.default_llm_key(company_id=company_id,query=self.query,projection= self.projection,companymodel=companymodel)

            llm_apikey_decrypt_service.initialization(self.api_key_id, companymodel)
            self.encrypted_key = llm_apikey_decrypt_service.apikey
            self.companyRedis_id=llm_apikey_decrypt_service.companyRedis_id
            self.model_name=llm_apikey_decrypt_service.model_name
            
            self.llm = ChatGoogleGenerativeAI(model=llm_apikey_decrypt_service.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temprature',0.7),
                google_api_key=llm_apikey_decrypt_service.decrypt(),
                disable_streaming=False,
                verbose=False,
                max_tokens=None)
            self.llm_non_stream = ChatGoogleGenerativeAI(model=GEMINIMODEL.DEFAULT_TOOL_MODEL,
                temperature=llm_apikey_decrypt_service.extra_config.get('temprature',0.7),
                google_api_key=llm_apikey_decrypt_service.decrypt(),
                disable_streaming=True,
                verbose=False)
                
            self.tools = [self.simple_run_conversation, self.wrapper_website_analysis]
            self.llm_with_tools = self.llm_non_stream.bind_tools(
            self.tools, tool_choice='any')
            self.query_arguments = {'simple_run_conversation':{}}
       
       
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
    def initialize_memory(self):
        """
        Sets up the memory component using ConversationSummaryBufferMemory.

        Exceptions
        ----------
        Logs an error if the memory initialization fails.
        """
        try:
            self.memory = ConversationSummaryBufferMemory(
                memory_key="history",
                input_key="input",
                llm=self.llm_non_stream,
                max_token_limit=CustomGptChatConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.initialize_memory"}}
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
        ValueErrordoc
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
                        "tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.prompt_attach"},
                        "additional_prompt_id": additional_prompt_id,
                        "collection_name": collection_name})
                else:
                    self.additional_prompt = None
            else:
                self.additional_prompt = None
        except Exception as e:
            logger.error(
                f"Failed to prompt attach: {e}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.prompt_attach"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to prompt attach: {e}")


    def create_conversation(self,input_text:str,**kwargs):
        """
        Creates a conversation chain with a custom tag.

        Parameters
        ----------
        input_text : str
            A user input query

        Exceptions
        ----------
        Logs an error if the conversation creation fails.
        """
        try:
            
            if kwargs.get("regenerated_flag"):
                input_text = " Regenerate the above response with improvements in clarity, relevance, and depth as needed. Adjust the level of detail based on the query's requirements—providing a concise response when appropriate and a more detailed, expanded answer when necessary." + input_text
            self.user_agent_name=custom_gpt_repo.get_name()
            self.user_system_prompt=custom_gpt_repo.get_gpt_system_prompt()
            self.user_goals=custom_gpt_repo.get_gpt_goals()
            self.user_instructions=custom_gpt_repo.get_gpt_instructions()
            user_custom_prompt.initialization(user_agent_name=self.user_agent_name, \
                                              user_system_prompt=self.user_system_prompt,user_goals=self.user_goals,user_instructions=self.user_instructions)
            self.inputs={"input": input_text}
            self.image_url = kwargs.get('image_url', None)
            if self.image_url is not None and self.model_name in GEMINIMODEL.VISION_MODELS:
                messages=user_custom_prompt.create_chat_prompt_image(additional_prompt=self.additional_prompt)
                if isinstance(self.image_url, str):
                    self.image_url = [self.image_url]
                for idx, url in enumerate(self.image_url, start=1):
                    messages.append(HumanMessagePromptTemplate.from_template(template=[
                        {"type": "image_url", "image_url":{"url": f"{{image_url{idx}}}"}},]))
                    self.inputs[f"image_url{idx}"] = url
                    
                self.prompt = ChatPromptTemplate.from_messages(messages)
                
            else:
                self.prompt = user_custom_prompt.create_chat_prompt(additional_prompt=self.additional_prompt)
                
            self.conversation = CustomConversationChain(
                prompt=self.prompt,
                llm=self.llm,
                memory=self.memory,
                verbose=False,
                
            )
        except Exception as e:
            logger.error(
                f"Failed to create conversation: {e}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.create_conversation"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create conversation: {e}")
    def _get_inputs(self):
        return self.inputs
    

    async def tool_calls_run(self, thread_id: str, collection_name: str,regenerated_flag=False, msgCredit=0,is_paid_user=False,**kwargs) -> AsyncGenerator[str, None]:
        """
        Executes a conversation and updates the token usage and conversation history.

        Parameters
        ----------
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
         
            self.thread_id = thread_id
            self.collection_name = collection_name
            self.regenerated_flag = regenerated_flag
            self.msgCredit = msgCredit
            self.is_paid_user=is_paid_user
            self.kwargs = kwargs
      
            self.delay_chunk = kwargs.get("delay_chunk", 0.0)
            with gemini_sync_cost_handler(model_name=self.model_name) as cb:
                tool_history=self.chat_repository_history.messages
                
                tool_history.insert(0,SystemMessage(user_custom_prompt.get_user_system_prompt()))
                tool_history.append(HumanMessage(self.inputs['input']))
                self.original_query=self.inputs['input']
                ai_msg = self.llm_with_tools.invoke(tool_history)
                # await self.api_usage_service.update_usage(provider=llm_apikey_decrypt_service.bot_data.get('code', 'GEMINI'),tokens_used= cb.total_tokens, model=self.model_name, api_key=llm_apikey_decrypt_service.apikey,functionality=Functionality.CHAT,company_id=self.companyRedis_id)
            for tool_call in ai_msg.tool_calls:
                selected_tool = {tool.name.lower(): tool for tool in self.tools}[
                    tool_call['name'].lower()]
         
                
                logger.info(f"Invoking tool: {selected_tool.name}", extra={
                "tags": {"method": "ToolStreamingService.tool_calls_run"}
            })

                if selected_tool.name == 'simple_run_conversation':
                    async for tool_output in self.simple_run_conversation_v1():
                        yield tool_output  # Process the streamed output here
                        await asyncio.sleep(self.delay_chunk)
                elif selected_tool.name == 'wrapper_website_analysis':
                    list_urls = []
                    for i in ai_msg.tool_calls:
                        x = i['args'].get('implicit_reference_urls', [])
                        list_urls.extend(x)
                    self.implicit_reference_urls = list_urls
                    async for tool_output in self.website_analysis():
                        yield tool_output
                        await asyncio.sleep(self.delay_chunk)
                break
            thread_repo.initialization(
                thread_id=thread_id, collection_name=collection_name)
            thread_repo.update_token_usage(cb=cb)

        except ResourceExhausted as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.ResourceExhausted"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("resource_exhausted_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except GoogleAPICallError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.GoogleAPICallError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("google_api_call_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_call_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        # Handle GoogleAPIError
        except GoogleAPIError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.GoogleAPIError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("google_api_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except GoogleGenerativeAIError as e:
            error_content = extract_google_genai_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.GoogleGenerativeAIError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("google_genai_error")

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
                        extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.Exception.extract_google_error_message"}})

                # If no content from the first extractor, try the second one
                if not error_content:
                    try:
                        error_content = extract_google_genai_error_message(str(e))
                    except Exception as inner_e:
                        logger.warning(
                            f"Warning: Failed to extract using extract_google_genai_error_message: {inner_e}",
                            extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.Exception.extract_google_genai_error_message"}})

                # Default error message if extraction fails
                if not error_content:
                    error_content = DEV_MESSAGES_CONFIG.get("genai_message")

                logger.error(
                    f"🚨 Failed to stream run conversation: {error_content}",
                    extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.Exception_Try"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  

            except Exception as inner_e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {inner_e}",
                    extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.Exception_Except"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST

    @tool(description=ToolServiceDescription.SIMPLE_CHAT)
    async def simple_run_conversation(self) -> AsyncGenerator[str, None]:
        pass
    
    @tool(description=ToolServiceDescription.WEB_ANALYSIS)
    async def wrapper_website_analysis(self,implicit_reference_urls:list[str]=[],**kwargs):
        pass
    
    async def website_analysis(self,**kwargs):
        try:
            logger.info(f"Tool 'website_analysis' called", extra={"tags": {"method": "GeminiCustomGPTStreamingDocChatServiceImg.website_analysis"}})
            self.implicit_reference_urls = [domain for item in self.implicit_reference_urls for domain in item.split(",")]
            urls = re.findall(r'https?://[^\s"\'>)]+', self.original_query)
            urls.extend(self.implicit_reference_urls)

            urls = list(set(urls))  # Remove duplicates
            thread_id=self.thread_id
            thread_model=self.collection_name
        
            # web_content=await scraping_service.multiple_crawl_and_clean(urls=urls)
            if len(urls)> 0:
                web_content = crawler_scraper_task.apply_async(kwargs={'urls': urls}).get()
            else:
                web_content= '' 
            
            llm = ChatGoogleGenerativeAI(model=llm_apikey_decrypt_service.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temprature',0.7),
                google_api_key=llm_apikey_decrypt_service.decrypt(),
                disable_streaming=False,
                verbose=False)
            self.model_name=llm_apikey_decrypt_service.model_name
            prompt_list = self.chat_repository_history.messages
            prompt_list.append(HumanMessagePromptTemplate.from_template(template=[{"type": "text", "text": '{query}'}]))
            web_query_input = {"query":self.original_query}
            if web_content:
                prompt_list.append(HumanMessagePromptTemplate.from_template(template=[{"type": "text", "text": '{web_content}'}]))
                web_query_input.update({"web_content": web_content})           
            chat_prompt = ChatPromptTemplate.from_messages(prompt_list)

            llm_chain = LLMChain(llm=llm, prompt=chat_prompt)
            max_chunk_size = 5  # Set your desired chunk size

            async with  \
                    gemini_async_cost_handler(model_name=self.model_name, thread_id=thread_id, collection_name=thread_model,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as cb, \
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=thread_model,model_name=self.model_name,regenerated_flag=self.regenerated_flag,msgCredit=self.msgCredit,is_paid_user=self.is_paid_user,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as mongo_handler:
                        # Stream the response
                    event_stream = llm_chain.astream_events(web_query_input, {"callbacks": [cb, mongo_handler]}, version="v1", stream_usage=True)
                    stream_iter = event_stream.__aiter__()


                    async for token in stream_iter:
                        if token['event']=="on_chat_model_stream":
                           
                            chunk=token['data']['chunk'].content
                            for i in range(0, len(chunk), max_chunk_size):
                                small_chunk = chunk[i:i + max_chunk_size]
                                small_chunk = small_chunk.encode("utf-8")
                                yield f"data: {small_chunk}\n\n", 200
                                
        except ResourceExhausted as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.website_analysis.ResourceExhausted"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_gemini("resource_exhausted_error")
            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except GoogleAPICallError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.website_analysis.GoogleAPICallError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_gemini("google_api_call_error")
            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_call_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        # Handle GoogleAPIError
        except GoogleAPIError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.website_analysis.GoogleAPIError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_gemini("google_api_error")
            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except GoogleGenerativeAIError as e:
            error_content = extract_google_genai_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.website_analysis.GoogleGenerativeAIError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_gemini("google_genai_error")
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
                        extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.Exception.extract_google_error_message"}})
                # If no content from the first extractor, try the second one
                if not error_content:
                    try:
                        error_content = extract_google_genai_error_message(str(e))
                    except Exception as inner_e:
                        logger.warning(
                            f"Warning: Failed to extract using extract_google_genai_error_message: {inner_e}",
                            extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.Exception.extract_google_genai_error_message"}})
                # Default error message if extraction fails
                if not error_content:
                    error_content = DEV_MESSAGES_CONFIG.get("genai_message")
                logger.error(
                    f"🚨 Failed to stream run conversation: {error_content}",
                    extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.website_analysis.Exception_Try"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
            except Exception as inner_e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {inner_e}",
                    extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.website_analysis.Exception_Except"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST

    async def simple_run_conversation_v1(self) -> AsyncGenerator[str, None]:
        """
        simple conversation for use this tool
        
        """
        try:
            
            thread_id=self.thread_id
            collection_name=self.collection_name
            self.delay_chunk=self.kwargs.get("delay_chunk",0.0)

            async with gemini_async_cost_handler(model_name=llm_apikey_decrypt_service.model_name, thread_id=thread_id, collection_name=collection_name,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id,**self.kwargs) as cb, \
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=collection_name,regenerated_flag=self.regenerated_flag,model_name=llm_apikey_decrypt_service.model_name,msgCredit=self.msgCredit,is_paid_user=self.is_paid_user,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as mongo_handler:

                async for token in self.conversation.astream_events(self.inputs,{"callbacks":[cb,mongo_handler]},version="v1",stream_usage=True):
                    if token['event']=="on_chat_model_stream":
                        max_chunk_size = 5  # Set your desired chunk size
                        chunk=token['data']['chunk'].content
                        for i in range(0, len(chunk), max_chunk_size):
                            small_chunk = chunk[i:i + max_chunk_size]
                            small_chunk = small_chunk.encode("utf-8")
                            yield f"data: {small_chunk}\n\n", 200
                            await asyncio.sleep(self.delay_chunk)
                    else:
                        pass
                    # cleaned_token = token.replace('"', '')  
                    # yield f"data: {json.dumps(cleaned_token)}\n\n",200

        except ResourceExhausted as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.ResourceExhausted"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("resource_exhausted_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("resource_exhausted_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except GoogleAPICallError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.GoogleAPICallError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("google_api_call_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_call_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        # Handle GoogleAPIError
        except GoogleAPIError as e:
            error_content = extract_google_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.GoogleAPIError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("google_api_error")

            # llm_apikey_decrypt_service.update_deprecated_status(True)
            content = GENAI_ERROR_MESSAGES_CONFIG.get("google_api_error", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except GoogleGenerativeAIError as e:
            error_content = extract_google_genai_error_message(str(e))
            logger.error(
                f"🚨 Google API Error: {error_content}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.GoogleGenerativeAIError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_gemini("google_genai_error")

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
                        extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.Exception.extract_google_error_message"}})

                # If no content from the first extractor, try the second one
                if not error_content:
                    try:
                        error_content = extract_google_genai_error_message(str(e))
                    except Exception as inner_e:
                        logger.warning(
                            f"Warning: Failed to extract using extract_google_genai_error_message: {inner_e}",
                            extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.Exception.extract_google_genai_error_message"}})

                # Default error message if extraction fails
                if not error_content:
                    error_content = DEV_MESSAGES_CONFIG.get("genai_message")

                logger.error(
                    f"🚨 Failed to stream run conversation: {error_content}",
                    extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.Exception_Try"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response", GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  

            except Exception as inner_e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {inner_e}",
                    extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.tool_calls_run.Exception_Except"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_gemini("common_response")
                content = GENAI_ERROR_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("genai_message"), "data": content}), status.HTTP_400_BAD_REQUEST

        finally:
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
                'conversation',
                'inputs',
                'additional_prompt',
                'chat_repository_history',
                'conversation_summary_buffer_memory',
                'cost_calculator',
                'async_handler',
                'mongodb_handler',
                'custom_openai_callback',
                'api_usage_service'
            ]

            for attr in attributes:
                if hasattr(self, attr):
                    delattr(self, attr)  # Deletes the attribute from the instance
                    cleaned_up.append(attr)  # Adds the attribute name to the cleaned_up list

            gc.collect()  # Force garbage collection to free memory

            # Log a single message with the list of cleaned-up attributes
            if cleaned_up:
                logger.info(
                    f"Successfully cleaned up resources: {', '.join(cleaned_up)}.",
                    extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "GeminiCustomGPTStreamingSimpleChatServiceTool.cleanup"}}
            )

    async def test(self):
        """
        A simple test method to yield test events.
        """
        yield "event: streaming\ndata: Initial connection established\n\n"
        await asyncio.sleep(0.2)
        
        for words in ['k', 'a', 'b', 'c', 'd']:
            yield f"event: streaming\ndata: {words}\n\n"
            await asyncio.sleep(0.2)
