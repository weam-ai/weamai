import asyncio
import json
from langchain_core.tools import tool
from bson.objectid import ObjectId
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.callbacks.manager import get_openai_callback
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from typing import AsyncGenerator
from src.logger.default_logger import logger
from src.chatflow_langchain.service.o1.custom_gpt.config import ToolChatConfig
from src.chat.service.base.abstract_conversation_service import AbstractConversationService
from src.vector_store.qdrant.langchain_lib.qdrant_store import QdrantVectorStoreService
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.o1_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.chatflow_langchain.service.o1.custom_gpt.doc.chat_prompt_factory import UserCustomGPTPrompt
from fastapi import HTTPException, status
from src.chatflow_langchain.repositories.custom_gpt_repository import CustomGPTRepository
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.openai.cost.context_manager import get_custom_openai_callback
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.openai.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.openai.streaming.custom_stream_async_handler import CustomAsyncIteratorCallbackHandler
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError, NotFoundError
from src.chatflow_langchain.service.o1.custom_gpt.config import CustomGptDocConfig,GetLLMkey,DEFAULTMODEL
from src.chatflow_langchain.utils.fill_additional_prompt import fill_template, format_website_summary_pairs
import gc
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.chatflow_langchain.service.o1.custom_gpt.doc.utils import extract_error_message
from src.chatflow_langchain.repositories.chatdocs_repo import ChatDocsRepository
from src.chatflow_langchain.service.o1.custom_gpt.doc.tools import image_generate
from src.celery_worker_hub.web_scraper.tasks.scraping_sitemap import crawler_scraper_task
from langchain_core.messages import SystemMessage, HumanMessage
from src.chatflow_langchain.service.config.model_config_openai import DefaultGPTTextModelRepository, OPENAIMODEL,WebSearchConfig
from langchain.chains import LLMChain
import re
from src.chatflow_langchain.utils.playwright_info_fetcher import LogoFetcherService
from src.chatflow_langchain.service.o1.config.o1_tool_description import ToolDescritpion
from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_openai import Functionality
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
qdrant_vector_store= QdrantVectorStoreService()
prompt_repo = PromptRepository()
custom_gpt_repo = CustomGPTRepository()
user_custom_prompt = UserCustomGPTPrompt()
chat_docs = ChatDocsRepository()

class O1CustomGPTStreamingDocChatServiceImg(AbstractConversationService):
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
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatService.Initilization_custom_gpt"}}
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
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.initialize_repository"}}
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
            self.api_usage_service= APIKeyUsageService()
            if kwargs.get("regenerated_flag"):
                self.api_key_id=kwargs.get('llm_apikey')
            else:
                self.api_key_id=custom_gpt_repo.get_gpt_llm_key_id()
            if self.api_key_id is None:
                get_key=GetLLMkey()
                self.query = {
                    "name": OPENAIMODEL.GPT_4_1_MINI,
                    "company.id": ObjectId(company_id)
                    }
                self.projection = {
                        '_id': 1
                    }
                self.api_key_id = get_key.default_llm_key(company_id=company_id,query=self.query,projection= self.projection,companymodel=companymodel)

            llm_apikey_decrypt_service.initialization(self.api_key_id, companymodel)
            self.companyRedis_id=llm_apikey_decrypt_service.companyRedis_id
            self.encrypted_key=llm_apikey_decrypt_service.apikey
            self.model_name = llm_apikey_decrypt_service.model_name
            self.callback_handler = CustomAsyncIteratorCallbackHandler() 
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature',1),
                api_key=llm_apikey_decrypt_service.decrypt(),
                streaming=True,
                verbose=False,
                callbacks=[self.callback_handler],
                use_responses_api=True,
                stream_usage=True
            )
            self.llm_non_stream = ChatOpenAI(
                model_name=OPENAIMODEL.DEFAULT_TOOL_MODEL,
                temperature=1,
                api_key=llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False,
                use_responses_api=True,
                stream_usage=True
            )
            self.llm_sum_memory = ChatOpenAI(
                model_name=self.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False,
                use_responses_api=True,
                stream_usage=True
            )
            if self.model_name in WebSearchConfig.MODEL_LIST:
                self.tools = [self.wrapper_rag_conversation,self.wrapper_web_search_preview]
            else:
                self.tools = [self.wrapper_rag_conversation,self.wrapper_website_analysis]
            img_flag=custom_gpt_repo.get_img_flag()
            if img_flag:
                self.tools.append(image_generate)
            self.temperature = llm_apikey_decrypt_service.extra_config.get('temperature')
            self.llm_with_tools = self.llm_non_stream.bind_tools(
            self.tools, tool_choice='any',strict=False)
            self.query_arguments = {'wrapper_rag_conversation':{},
                                'image_generate': {'model_name': OPENAIMODEL.LLM_IMAGE_MODEL, 'n': OPENAIMODEL.n, 'image_quality': OPENAIMODEL.DALLE_WRAPPER_QUALITY, 'image_size': OPENAIMODEL.DALLE_WRAPPER_SIZE, 'image_style': OPENAIMODEL.DALLE_WRAPPER_STYLE, 'openai_api_key': llm_apikey_decrypt_service.decrypt(),'api_key_id': self.api_key_id,'llm_model':self.model_name,'encrypted_key':self.encrypted_key,'companyRedis_id':self.companyRedis_id}}
       
            
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.initialize_llm"}}
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
                memory_key="chat_history",
                input_key="question",
                output_key="answer",
                llm=self.llm_sum_memory,
                max_token_limit=CustomGptDocConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
            self.query_arguments['image_generate'].update(
                {'memory': self.memory})
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.initialize_memory"}}
            )
        
    def load_vector_store(
        self,
        namespace: str = 'uwp',
        companypinecone_collection: str = None,
        company_model_collection: str = None,
        text_fieled: str = 'text',
        company_apikey_id: str = None,
        chat_doc_collection="chatdocs",
        query: str = None,
        **kwargs
    ):
        """
        Loads the vector store with the specified configurations.

        Parameters
        ----------
        
        namespace : str, optional
            The namespace for the vector store.
        companypinecone_collection : str, optional
            The Pinecone collection for the company.
        company_apikey_id : str, optional
        company_model_collection : str, optional
            The model collection for the company.
        text_fieled : str, optional
            The text field to be used, default is 'text'.

        Exceptions
        ----------
        Logs an error if the vector store loading fails.
        """
        try:
            namespace = custom_gpt_repo.get_gpt_brain_id()
            # namespace=namespace
            self.tag=custom_gpt_repo.get_gpt_file_tag_list()
            self.file_ids = custom_gpt_repo.get_gpt_file_ids()
            embedder_api_key_id=custom_gpt_repo.get_gpt_embedding_key()
            if embedder_api_key_id is None:
                embedder_model=DefaultGPTTextModelRepository(company_id=company_apikey_id,companymodel=company_model_collection)
                embedder_api_key_id=str(embedder_model.get_default_model_key())
            qdrant_vector_store.initialization(
                company_apikey_id=company_apikey_id,
                namespace=namespace,
                embedder_api_key_id=embedder_api_key_id,
                companypinecone_collection=companypinecone_collection,
                company_model_collection=company_model_collection,
                text_field=text_fieled,
            

            )
            self.extract_files_data(kwargs)
            chat_docs.initialization(file_id_list=self.file_ids,collection_name=chat_doc_collection)
            namespace_list = chat_docs.get_brain_id_list()
            self.vectorstore = qdrant_vector_store.get_lot_retiver_namespace(top_k=CustomGptDocConfig.TOP_K,tag_list=self.tag,namespace_list=namespace_list, query=query, companymodel=company_model_collection, company_id=company_apikey_id)
        except Exception as e:
            logger.error(
                f"Failed to load vector store: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.load_vector_store"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to load vector store: {e}")
    def extract_files_data(self, kwargs):
        extra_file_ids = kwargs.get('extra_files_ids', [])
        extra_tags=kwargs.get("extra_tags",[])
        if extra_file_ids:
            self.file_ids += extra_file_ids
            self.tag += extra_tags
        
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
                        "tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.prompt_attach"},
                        "additional_prompt_id": additional_prompt_id,
                        "collection_name": collection_name})
                else:
                    self.additional_prompt = None
            else:
                self.additional_prompt = None
        except Exception as e:
            logger.error(
                f"Failed to prompt attach: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.prompt_attach"}}
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
            # self.tag = custom_gpt_repo.get_gpt_file_tag()
            user_agent_name=custom_gpt_repo.get_name()
            user_system_prompt=custom_gpt_repo.get_gpt_system_prompt()
            user_goals=custom_gpt_repo.get_gpt_goals()
            user_instructions=custom_gpt_repo.get_gpt_instructions()
            user_custom_prompt.initialization(user_agent_name=user_agent_name, \
                                              user_system_prompt=user_system_prompt,user_goals=user_goals,user_instructions=user_instructions)
            self.result=[]
            self.inputs={"question": input_text}
            self.image_url = kwargs.get('image_url', None)
            self.messages = user_custom_prompt.create_chat_prompt_doc(additional_prompt=self.additional_prompt)
            if self.image_url is not None and self.model_name in OPENAIMODEL.VISION_MODELS:
                
                if isinstance(self.image_url, str):
                    self.image_url = [self.image_url]
                for idx, url in enumerate(self.image_url, start=1):
                    self.messages.append(HumanMessagePromptTemplate.from_template(template=[
                        {"type": "image_url", "image_url":{"url": f"{{image_url{idx}}}"}},]))
                    self.inputs[f"image_url{idx}"] = url
                
                for i in self.image_url:
                    parts = i.strip("/").split("/")
                    self.result.append("/".join(parts[-2:]))
                self.query_arguments['image_generate']['image_url'] = self.image_url

            self.prompt = ChatPromptTemplate.from_messages(self.messages)
            
            self.conversational_retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore,
                chain_type="stuff",
                combine_docs_chain_kwargs={'prompt': self.prompt},
                return_source_documents=False,
                memory=self.memory,
                condense_question_llm=self.llm_non_stream,
                verbose=False,
                rephrase_question=False
            )
        except Exception as e:
            logger.error(
                f"Failed to create conversation: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.create_conversation"}}
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
            self.msgCredit=msgCredit
            self.is_paid_user=is_paid_user
            self.kwargs = kwargs
            self.temp_store=qdrant_vector_store
            delay_chunk = kwargs.get("delay_chunk", 0.0)
            with get_openai_callback() as cb:
                tool_history=self.chat_repository_history.messages
                
                tool_history.insert(0,SystemMessage(user_custom_prompt.get_user_system_prompt()))
                tool_history.append(HumanMessage(self.inputs['question']+' '.join(self.result)))
                self.original_query=self.inputs['question']
                ai_msg = self.llm_with_tools.invoke(tool_history)
                if ai_msg.tool_calls[0]['name'] == 'image_generate':
                    image_size = ai_msg.tool_calls[0]['args'].get('image_size','1024x1024')
                    edit_flag = ai_msg.tool_calls[0]['args'].get('editHistory_flag',False)
                    self.query_arguments['image_generate']['editHistory_flag'] = edit_flag
                    if image_size in ToolChatConfig.IMAGE_SIZE_LIST:
                        self.query_arguments['image_generate']['image_size']=image_size
            # await self.api_usage_service.update_usage(provider=llm_apikey_decrypt_service.bot_data.get('code', 'OPEN_AI'),tokens_used= cb.total_tokens, model=self.model_name, api_key=llm_apikey_decrypt_service.apikey,functionality=Functionality.CHAT,company_id=self.companyRedis_id)
            for tool_call in ai_msg.tool_calls:
                selected_tool = {tool.name.lower(): tool for tool in self.tools}[
                    tool_call['name'].lower()]
         
                
                logger.info(f"Invoking tool: {selected_tool.name}", extra={
                "tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.tool_calls_run"}
            }) 
                if selected_tool.name == 'image_generate':
                   
                    self.temp_store=qdrant_vector_store
                    self.query_arguments['image_generate']["chat_repository_history"]= self.chat_repository_history
                    self.query_arguments['image_generate']['regenerated_flag']=regenerated_flag
                    self.query_arguments['image_generate']['msgCredit']=msgCredit
                    self.query_arguments['image_generate']['is_paid_user']=is_paid_user
                    self.query_arguments['image_generate']['thread_id']=thread_id
                    self.query_arguments['image_generate']['thread_model']=collection_name
                    self.query_arguments['image_generate']['original_query']=self.inputs['question']
                    self.query_arguments['image_generate']['user_system_prompt']=user_custom_prompt.get_user_system_prompt()
                    self.query_arguments['image_generate']['qdrant_vector_store']=self.temp_store
                    self.query_arguments['image_generate']['encrypted_key']=self.encrypted_key
                    self.query_arguments['image_generate']['companyRedis_id']=self.companyRedis_id
                    async for tool_output in selected_tool(self.query_arguments[selected_tool.name]):
                        yield tool_output  # Process the streamed output here
                        await asyncio.sleep(delay_chunk)
                
                elif selected_tool.name == 'wrapper_rag_conversation':
                    async for tool_output in self.rag_run_conversation():
                        yield tool_output  # Process the streamed output here
                        await asyncio.sleep(delay_chunk)
                elif selected_tool.name == 'wrapper_web_search_preview':
                    async for tool_output in self.web_search_preview():
                        yield tool_output
                        await asyncio.sleep(delay_chunk)    
                elif selected_tool.name == 'wrapper_website_analysis':
                    list_urls = []
                    for i in ai_msg.tool_calls:
                        x = i['args'].get('implicit_reference_urls', [])
                        list_urls.extend(x)
                    self.implicit_reference_urls = list_urls
                    async for tool_output in self.website_analysis():
                        yield tool_output
                        await asyncio.sleep(delay_chunk)
                break
            thread_repo.initialization(
                thread_id=thread_id, collection_name=collection_name)
            thread_repo.update_token_usage(cb=cb)

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.tool_calls_run.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.tool_calls_run.NotFoundError"}})
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
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.tool_calls_run.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.tool_calls_run.RateLimitError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
   
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.tool_calls_run.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.tool_calls_run.APIStatusError"}})
                thread_repo.initialization(self.thread_id, collection_name)
                thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    @tool(description=ToolDescritpion.RAG_CONVERSATION)
    def wrapper_rag_conversation(self, input_text: str, **kwargs):
        pass
    @tool(description=ToolDescritpion.WEB_SEARCH_PREVIEW)
    def wrapper_web_search_preview(self, input_text: str, **kwargs):
        pass
    
    @tool(description=ToolDescritpion.WEB_ANALYSIS)
    async def wrapper_website_analysis(self,implicit_reference_urls:list[str]=[],**kwargs):
        pass


    async def web_search_preview(self):
        try:
            logger.info(f"Tool 'web_search_preview' called", extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview"}})
            chunk=self.temp_store.multi_doc_query(query_text=self.original_query)
            thread_id=self.thread_id
            thread_model=self.collection_name
            self.astream_llm = ChatOpenAI(temperature=llm_apikey_decrypt_service.extra_config.get('temperature'),
                    api_key=llm_apikey_decrypt_service.decrypt(),
                                model=self.model_name, streaming=True, stream_usage=True,use_responses_api=True)
            search_context_size=WebSearchConfig.SEARCH_CONTEXT_SIZE
            tool = {"type": "web_search_preview", "search_context_size":search_context_size}
            self.astream_llm_with_tools = self.astream_llm.bind_tools([tool])
            prompt_list = self.chat_repository_history.messages
            prompt_list.append(HumanMessagePromptTemplate.from_template(template=[{"type": "text", "text": '{query}'}]))
            prompt_list.append(HumanMessagePromptTemplate.from_template(template=[{"type": "text", "text": '\n document reference_chunks {chunk}'}]))


            chat_prompt = ChatPromptTemplate.from_messages(prompt_list)

            web_query_input = {"query": self.original_query,"chunk":chunk}  # Single query

            llm_chain = LLMChain(llm=self.astream_llm_with_tools, prompt=chat_prompt)
            cost_callback = CostCalculator()
            annotations=[]
            async with  \
                    get_custom_openai_callback(self.model_name, cost=cost_callback, thread_id=self.thread_id, collection_name=thread_model,search_context_size=search_context_size,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as cb, \
                    get_mongodb_callback_handler(thread_id=self.thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=thread_model,regenerated_flag=self.regenerated_flag,msgCredit=self.msgCredit,is_paid_user=self.is_paid_user,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as mongo_handler:
                        # Stream the response
                    event_stream = llm_chain.astream_events(web_query_input, {"callbacks": [cb, mongo_handler]}, version="v1", stream_usage=True)
                    stream_iter = event_stream.__aiter__()


                    async for token in stream_iter:
                        if token['event'] == "on_chat_model_end":
                            if annotations:
                                try:
                                    fetcher = LogoFetcherService()
                                    citations_results = await fetcher.get_logos_async(annotations)
                                    citations_section = {"web_resources_data": citations_results}
                                    compact_json = json.dumps(citations_section, separators=(',', ':'))
                                    data_string = f"data: {compact_json.encode('utf-8')}\n\n"
                                except Exception as e:
                                    error_response = {"web_resources_data": []}
                                    compact_json = json.dumps(error_response, separators=(',', ':'))
                                    data_string = f"data: {compact_json.encode('utf-8')}\n\n"
                                yield data_string, 200
                            continue

                        if token['event'] != "on_chat_model_stream":
                            continue

                        chunk = token['data']['chunk'].content
                        if not chunk:
                            continue

                        content = chunk[0]

                        # Stream text if available
                        if 'text' in content:
                            text_chunk = content['text']
                            yield f"data: {text_chunk.encode('utf-8')}\n\n", 200

                        # Collect annotations if available
                        elif 'annotations' in content:
                            for ann in content['annotations']:
                                annotations.append(ann['url'])
        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.NotFoundError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)

            llm_apikey_decrypt_service.initialization(self.api_key_id,"companymodel")
            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.RateLimitError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS

        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.APIStatusError"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.APIStatusError"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.LengthFinishReasonError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.ContentFilterFinishReasonError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.APITimeoutError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.APIConnectionError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in OPENAI_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.Exception_Try"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.Exception_Try"}})
                    thread_repo.initialization(thread_id, thread_model)
                    thread_repo.add_message_openai("connection_error")
                    content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
                    yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
                except Exception as e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.web_search_preview.Exception_Except"}})
                    thread_repo.initialization(thread_id, thread_model)
                    thread_repo.add_message_openai("common_response")
                    content = OPENAI_MESSAGES_CONFIG.get("common_response")
                    yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST
                    

        


    async def website_analysis(self,**kwargs):
        try:
            logger.info(f"Tool 'website_analysis' called", extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis"}})
            chunk=self.temp_store.multi_doc_query(query_text=self.original_query)
            self.implicit_reference_urls = [domain for item in self.implicit_reference_urls for domain in item.split(",")]
            urls = re.findall(r'https?://[^\s"\'>)]+', self.original_query)
        
            urls.extend(self.implicit_reference_urls)

            urls = list(set(urls))  # Remove duplicates
            thread_id=self.thread_id
            thread_model=self.collection_name
            cost_callback = CostCalculator()
        
            # web_content=await scraping_service.multiple_crawl_and_clean(urls=urls)
            if len(urls)> 0:
                web_content = crawler_scraper_task.apply_async(kwargs={'urls': urls}).get()
            else:
                web_content= '' 
            
            llm = ChatOpenAI(temperature=self.temperature, api_key=llm_apikey_decrypt_service.decrypt(),
                                model=self.model_name, streaming=True, stream_usage=True,use_responses_api=True)
            prompt_list = self.chat_repository_history.messages
            prompt_list.append(HumanMessagePromptTemplate.from_template(template=[{"type": "text", "text": '{query}'}]))
            web_query_input = {"query": self.original_query,"chunk":chunk}  
            if web_content:
                prompt_list.append(HumanMessagePromptTemplate.from_template(template=[{"type": "text", "text": '{web_content}'}]))
                web_query_input.update({"web_content": web_content})            
            prompt_list.append(HumanMessagePromptTemplate.from_template(template=[{"type": "text", "text": '\n document reference_chunks {chunk}'}]))

           

            chat_prompt = ChatPromptTemplate.from_messages(prompt_list)


            llm_chain = LLMChain(llm=llm, prompt=chat_prompt)

            async with  \
                    get_custom_openai_callback(self.model_name, cost=cost_callback, thread_id=thread_id, collection_name=thread_model,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as cb, \
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=thread_model,regenerated_flag=self.regenerated_flag,msgCredit=self.msgCredit,is_paid_user=self.is_paid_user,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as mongo_handler:
                        # Stream the response
                    event_stream = llm_chain.astream_events(web_query_input, {"callbacks": [cb, mongo_handler]}, version="v1", stream_usage=True)
                    stream_iter = event_stream.__aiter__()


                    async for token in stream_iter:
                        if token['event'] != "on_chat_model_stream":
                            continue

                        chunk = token['data']['chunk'].content
                        if not chunk:
                            continue

                        content = chunk[0]

                        # Stream text if available
                        if 'text' in content:
                            text_chunk = content['text']
                            yield f"data: {text_chunk.encode('utf-8')}\n\n", 200

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.NotFoundError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)

            llm_apikey_decrypt_service.initialization(self.api_key_id,"companymodel")
            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.RateLimitError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS

        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.APIStatusError"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.APIStatusError"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.LengthFinishReasonError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.ContentFilterFinishReasonError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.APITimeoutError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.APIConnectionError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in OPENAI_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.Exception_Try"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.Exception_Try"}})
                    thread_repo.initialization(thread_id, thread_model)
                    thread_repo.add_message_openai("connection_error")
                    content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
                    yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
                except Exception as e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.website_analysis.Exception_Except"}})
                    thread_repo.initialization(thread_id, thread_model)
                    thread_repo.add_message_openai("common_response")
                    content = OPENAI_MESSAGES_CONFIG.get("common_response")
                    yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

    async def rag_run_conversation(self) -> AsyncGenerator[str, None]:
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
            thread_id=self.thread_id
            collection_name=self.collection_name
            delay_chunk=self.kwargs.get("delay_chunk",0.0)
            cost = CostCalculator()

            async with  \
                    get_custom_openai_callback(self.model_name, cost=cost, thread_id=self.thread_id, collection_name=collection_name,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id,**self.kwargs) as cb, \
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=collection_name,regenerated_flag=self.regenerated_flag,msgCredit=self.msgCredit,is_paid_user=self.is_paid_user,encrypted_key=self.encrypted_key,companyRedis_id=self.companyRedis_id) as mongo_handler:

                run = asyncio.create_task(self.conversational_retrieval_chain.arun(
                    self._get_inputs(),
                    callbacks=[cb, mongo_handler]
                ))
                
                async for token in self.callback_handler.aiter():
                    data = token.encode("utf-8")
                    yield f"data: {data}\n\n",200
                    await asyncio.sleep(delay_chunk)
                    # yield f"data: {json.dumps(token)}\n\n",200
                await run
        
        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.NotFoundError"}})
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
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.RateLimitError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai(error_content)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS

        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.LengthFinishReasonError"}}
            )
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.ContentFilterFinishReasonError"}}
            )
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.APITimeoutError"}}
            )
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.APIConnectionError"}}
            )
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in OPENAI_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.Exception_Try"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation.Exception_Try"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.stream_run_conversation_Exception_Except"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

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
                'llm_sum_memory',
                'memory',
                'vectorstore',
                'conversational_retrieval_chain',
                'inputs',
                'additional_prompt',
                'callback_handler',
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
                    extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "O1CustomGPTStreamingDocChatServiceImg.cleanup"}}
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
