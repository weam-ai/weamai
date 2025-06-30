import asyncio
import json
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from typing import AsyncGenerator,Optional,Union
from src.logger.default_logger import logger
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from src.chat.service.base.abstract_conversation_service import AbstractConversationService
from src.vector_store.qdrant.langchain_lib.qdrant_store import QdrantVectorStoreService
from src.chatflow_langchain.service.multimodal_router.doc.chat_prompt_factory import create_chat_prompt_doc
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.file_repository import FileRepository
from src.chatflow_langchain.repositories.langchain_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.chatflow_langchain.repositories.chatdocs_repo import ChatDocsRepository
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.weam_router.open_router.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.weam_router.open_router.streaming.custom_stream_async_handler import CustomAsyncIteratorCallbackHandler
from src.chatflow_langchain.service.multimodal_router.doc.config import DocConfig
from src.chatflow_langchain.utils.fill_additional_prompt import fill_template, format_website_summary_pairs
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError, NotFoundError
from fastapi import HTTPException, status
import gc
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG,WEAM_ROUTER_MESSAGES_CONFIG
from src.chatflow_langchain.service.multimodal_router.doc.utils import extract_error_message
from src.chatflow_langchain.service.config.model_config_router import DefaultGPTTextModelRepository,ROUTERMODEL
from src.custom_lib.langchain.callbacks.weam_router.open_router.cost.context_manager import openrouter_async_callback
from langchain.chains import LLMChain

llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
qdrant_vector_store= QdrantVectorStoreService()
prompt_repo = PromptRepository()
file_repo = FileRepository()
chat_docs = ChatDocsRepository()

class RouterDocumentedService(AbstractConversationService):
    def initialize_llm(self, api_key_id: str = None, companymodel: str = None,thread_id:str=None,thread_model:str=None):
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
            llm_apikey_decrypt_service.initialization(api_key_id, companymodel)
            self.callback_handler = CustomAsyncIteratorCallbackHandler()
            self.model_name = llm_apikey_decrypt_service.model_name
            self.llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=llm_apikey_decrypt_service.extra_config.get(
                    'temperature'),
                    openai_api_key=llm_apikey_decrypt_service.decrypt(),
                    openai_api_base="https://openrouter.ai/api/v1",
                    streaming=True,
                    callbacks=[self.callback_handler],
                    model=ROUTERMODEL.GPT_4_1_MINI
                )
            self.llm_non_stream = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=llm_apikey_decrypt_service.extra_config.get(
                    'temperature'),
                    openai_api_key=llm_apikey_decrypt_service.decrypt(),
                    openai_api_base="https://openrouter.ai/api/v1",
                    streaming=False,
                    model=ROUTERMODEL.GPT_4_1_MINI
                )
            self.llm_sum_memory = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=llm_apikey_decrypt_service.extra_config.get(
                    'temperature'),
                    openai_api_key=llm_apikey_decrypt_service.decrypt(),
                    openai_api_base="https://openrouter.ai/api/v1",
                    streaming=False,
                    model=ROUTERMODEL.GPT_4_1_MINI
                )
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "RouterDocumentedService.initialize_llm"}}
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
            self.chat_repository_history = CustomAIMongoDBChatMessageHistory()
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
                extra={"tags": {"method": "RouterDocumentedService.initialize_repository"}}
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
                max_token_limit=DocConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "RouterDocumentedService.initialize_memory"}}
            )

    def load_vector_store(
        self,
        company_apikey_id: str = None,
        tag: Optional[Union[str, list[str]]] = None,
        namespace: str = None,
        companypinecone_collection: str = None,
        company_model_collection: str = None,
        text_fieled: str = 'text',
        file_id: Optional[Union[str, list[str]]] = None,
        file_collection:str=None,
        embedder_api_key_id: str = None,
        chat_doc_collection="chatdocs",
        query: str = None,
        **kwargs
    ):
        """
        Loads the vector store with the specified configurations.

        Parameters
        ----------
        company_apikey_id : str, optional
            The API key ID for company id.
        tag : str, optional
            A tag to filter the data.
        namespace : str, optional
            The namespace for the vector store.
        companypinecone_collection : str, optional
            The Pinecone collection for the company.
        company_model_collection : str, optional
            The model collection for the company.
        text_fieled : str, optional
            The text field to be used, default is 'text'.
        embedder_api_key_id : str, optional
            The API key ID for the embedder.

        Exceptions
        ----------
        Logs an error if the vector store loading fails.
        """
        try:
            if embedder_api_key_id is None:
                if isinstance(file_id,str):
                    file_repo.initialization(file_id=file_id,collection_name=file_collection)                 
                else:
                    file_repo.initialization(file_id=file_id[0],collection_name=file_collection)             
                embedder_api_key_id = file_repo.get_embedding_key()
                if embedder_api_key_id is None:
                    embedder_model=DefaultGPTTextModelRepository(company_id=company_apikey_id,companymodel=company_model_collection)
                    embedder_api_key_id=str(embedder_model.get_default_model_key())     
            
            if isinstance(file_id,str):
                chat_docs.initialization(file_id_list=[file_id],collection_name=chat_doc_collection)
            else:
                chat_docs.initialization(file_id_list=file_id,collection_name=chat_doc_collection)
            self.namespace_list = chat_docs.get_brain_id_list()

            qdrant_vector_store.initialization(
                company_apikey_id=company_apikey_id,
                namespace=namespace,
                embedder_api_key_id=embedder_api_key_id,
                companypinecone_collection=companypinecone_collection,
                company_model_collection=company_model_collection,
                text_field=text_fieled,
                
            )
            if isinstance(tag,str):
                self.vectorstore = qdrant_vector_store.get_lot_retiver_namespace(top_k=DocConfig.TOP_K,tag_list=[tag],namespace_list=self.namespace_list, query=query, companymodel=company_model_collection, company_id=company_apikey_id)
            else:
                self.vectorstore = qdrant_vector_store.get_lot_retiver_namespace(top_k=DocConfig.TOP_K,tag_list=tag,namespace_list=self.namespace_list, query=query, companymodel=company_model_collection, company_id=company_apikey_id)
        except Exception as e:
            logger.error(
                f"Failed to load vector store: {e}",
                extra={"tags": {"method": "RouterDocumentedService.load_vector_store"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to load vector store: {e}")
    
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
                        "tags": {"method": "RouterDocumentedService.prompt_attach"},
                        "additional_prompt_id": additional_prompt_id,
                        "collection_name": collection_name})
                else:
                    self.additional_prompt = None
            else:
                self.additional_prompt = None
        except Exception as e:
            logger.error(
                f"Failed to prompt attach: {e}",
                extra={"tags": {"method": "RouterDocumentedService.prompt_attach"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to prompt attach: {e}")

    def create_conversation(self,tag: str,input_text:str,**kwargs):
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
            if kwargs.get("regenerated_flag"):
                input_text = " Regenerate the above response with improvements in clarity, relevance, and depth as needed. Adjust the level of detail based on the query's requirements—providing a concise response when appropriate and a more detailed, expanded answer when necessary." + input_text

            
            self.chunks=qdrant_vector_store.multi_doc_query(query_text=input_text)
            self.tag = tag
            self.inputs={"question": input_text,"context":self.chunks}
            self.messages = create_chat_prompt_doc(chat_history=self.chat_repository_history.messages, additional_prompt=self.additional_prompt)
            self.image_url = kwargs.get("image_url", None)
            if self.image_url is not None and self.model_name in ROUTERMODEL.VISION_MODELS:
                if isinstance(self.image_url, str):
                    self.image_url = [self.image_url]
                for idx, url in enumerate(self.image_url, start=1):
                    self.messages.append(HumanMessagePromptTemplate.from_template(template=[
                        {"type": "image_url", "image_url":{"url": f"{{image_url{idx}}}"}},]))
                    self.inputs[f"image_url{idx}"] = url
            qa_prompt = ChatPromptTemplate.from_messages(self.messages)
            

            self.conversation = LLMChain(
                prompt=qa_prompt,
                llm=self.llm,
                verbose=False,
                
            )
            
            
        except Exception as e:
            logger.error(
                f"Failed to create conversation: {e}",
                extra={"tags": {"method": "RouterDocumentedService.create_conversation"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create conversation: {e}")
    
    def _get_inputs(self):
        return self.inputs

    async def stream_run_conversation(self, thread_id: str, collection_name: str,regenerated_flag:bool=False,msgCredit:float=0,is_paid_user:bool=False,**kwargs) -> AsyncGenerator[str, None]:
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
            async with  \
                    openrouter_async_callback(model_name=self.model_name,thread_id=thread_id,collection_name=collection_name) as cb,\
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=collection_name,regenerated_flag=regenerated_flag,model_name=self.model_name,msgCredit=msgCredit,is_paid_user=is_paid_user) as mongo_handler:

                run = asyncio.create_task(self.conversation.arun(
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
            if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.NotFoundError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router(error_code)

            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
 
        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.RateLimitError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router(error_code)
            content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
    
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_weam_router("common_response")
                content = WEAM_ROUTER_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_weam_router(error_code)
                content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.LengthFinishReasonError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router("content_filter_issue")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("content_filter_issue", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.ContentFilterFinishReasonError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router("content_filter_issue")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("content_filter_issue", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.APITimeoutError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router("request_time_out")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("request_time_out", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.APIConnectionError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router("connection_error")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("connection_error", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.Exception_Try"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.Exception_Try"}})
                    thread_repo.initialization(thread_id, collection_name)
                    thread_repo.add_message_weam_router(error_code)
                    content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
                    yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
                except Exception as e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "RouterDocumentedService.stream_run_conversation.Exception_Except"}})
                    thread_repo.initialization(thread_id, collection_name)
                    thread_repo.add_message_weam_router("common_response")
                    content = WEAM_ROUTER_MESSAGES_CONFIG.get("common_response")
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
                extra={"tags": {"method": "RouterDocumentedService.cleanup"}}
            )