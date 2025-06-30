import asyncio
import json
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from typing import AsyncGenerator
from src.logger.default_logger import logger
from src.chat.service.base.abstract_conversation_service import AbstractConversationService
from src.vector_store.qdrant.langchain_lib.qdrant_store import QdrantVectorStoreService
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.langchain_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.chatflow_langchain.service.huggingface.custom_gpt.doc.chat_prompt_factory import UserCustomGPTPrompt
from fastapi import HTTPException
from src.chatflow_langchain.repositories.custom_gpt_repository import CustomGPTRepository
from src.crypto_hub.services.huggingface.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.huggingface.cost.context_manager import get_custom_huggingface_callback
from src.custom_lib.langchain.callbacks.huggingface.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.huggingface.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.huggingface.streaming.custom_stream_async_handler import CustomAsyncIteratorCallbackHandler
from fastapi import status
from src.chatflow_langchain.service.huggingface.custom_gpt.config import CustomGptDocConfig
from src.chatflow_langchain.utils.fill_additional_prompt import fill_template,format_website_summary_pairs
import gc
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG,HF_ERROR_MESSAGES_CONFIG
from src.chatflow_langchain.service.huggingface.custom_gpt.doc.utils import extract_error_message
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from requests.exceptions import HTTPError
from huggingface_hub.utils import HfHubHTTPError, EntryNotFoundError, BadRequestError
from src.chatflow_langchain.repositories.chatdocs_repo import ChatDocsRepository
from src.chatflow_langchain.service.config.model_config_openai import DefaultGPTTextModelRepository
chat_docs=ChatDocsRepository()
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
qdrant_vector_store= QdrantVectorStoreService()
prompt_repo = PromptRepository()
custom_gpt_repo = CustomGPTRepository()
user_custom_prompt = UserCustomGPTPrompt()

class HFCustomGPTStreamingDocChatService(AbstractConversationService):
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
                extra={"tags": {"method": "CustomGPTStreamingDocChatService.Initilization_custom_gpt"}}
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
                extra={"tags": {"method": "CustomGPTStreamingDocChatService.initialize_repository"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initalize repository: {e}")

    def initialize_llm(self, company_id:str=None,companymodel: str = None,thread_id:str=None,thread_model:str=None,**kwargs):
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
            if kwargs.get("regenerated_flag"):
                api_key_id=kwargs.get('llm_apikey')
            else:
                api_key_id=custom_gpt_repo.get_gpt_llm_key_id()
            # if api_key_id is None:
            #     get_key=GetLLMkey()
            #     self.query = {
            #         "name": DEFAULTMODEL.GPT_4o_MINI,
            #         "company.id": ObjectId(company_id)
            #         }
            #     self.projection = {
            #             '_id': 1
            #         }
            #     api_key_id = get_key.default_llm_key(company_id=company_id,query=self.query,projection= self.projection,companymodel=companymodel)

            llm_apikey_decrypt_service.initialization(api_key_id, companymodel)

            self.callback_handler = CustomAsyncIteratorCallbackHandler() 
            self.llm_huggingface = HuggingFaceEndpoint(
                        endpoint_url=llm_apikey_decrypt_service.endpoint_url,
                        top_k=llm_apikey_decrypt_service.extra_config.get('topK',10),
                        top_p=llm_apikey_decrypt_service.extra_config.get('topP',0.95),
                        typical_p=llm_apikey_decrypt_service.extra_config.get('typicalP',0.95),
                        temperature=llm_apikey_decrypt_service.extra_config.get('temperature',0.7),
                        repetition_penalty=llm_apikey_decrypt_service.extra_config.get('repetitionPenalty',1.03),
                        streaming=llm_apikey_decrypt_service.streaming,
                        huggingfacehub_api_token=llm_apikey_decrypt_service.decrypt(),
                        stop_sequences=llm_apikey_decrypt_service.extra_config.get('stopSequences',['<|eot_id|>']),
                        max_new_tokens = CustomGptDocConfig.MAX_TOTAL_TOKENS
                    )
            self.thread_id=thread_id
            self.thread_model=thread_model
            self.validate_context_limits()
            self.llm_huggingface=ChatHuggingFace(llm=self.llm_huggingface,stop_sequences=llm_apikey_decrypt_service.extra_config.get('stopSequences'),callbacks=[self.callback_handler])
            self.llm_huggingface_non_stream = HuggingFaceEndpoint(
                        endpoint_url=llm_apikey_decrypt_service.endpoint_url,
                        top_k=llm_apikey_decrypt_service.extra_config.get('topK',10),
                        top_p=llm_apikey_decrypt_service.extra_config.get('topP',0.95),
                        typical_p=llm_apikey_decrypt_service.extra_config.get('typicalP',0.95),
                        temperature=llm_apikey_decrypt_service.extra_config.get('temperature',0.7),
                        repetition_penalty=llm_apikey_decrypt_service.extra_config.get('repetitionPenalty',1.03),
                        streaming=False,
                        huggingfacehub_api_token=llm_apikey_decrypt_service.decrypt(),
                        stop_sequences=llm_apikey_decrypt_service.extra_config.get('stopSequences',['<|eot_id|>'])
                    )
            self.llm_huggingface_non_stream=ChatHuggingFace(llm=self.llm_huggingface_non_stream,stop=llm_apikey_decrypt_service.extra_config.get('stopSequences',['<|eot_id|>']))
        except HTTPException as e:
            raise e
        except Exception as e:
            if "inference server" in str(e) or "model_id" in str(e):  
                # content = "Model ID not found or access denied."
                content = HF_ERROR_MESSAGES_CONFIG.get("hf_hub_http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
                message = DEV_MESSAGES_CONFIG.get('hugging_face_message')
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": message,
                        "data": content,
                        "platform":"HUGGING_FACE",
                        "error_code":'hf_hub_http_error'})
            else:
                content = "Initialization failed due to a value error"
                logger.error(f"Failed to initialize LLM: {e}",
                            extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.initialize_llm"}})
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")

    def validate_context_limits(self):
        """
        Validates the token limits between the configured max history tokens and the
        maximum input tokens supported by the Hugging Face endpoint. Raises an
        HTTPException if the token limits are insufficient.
        """

        try:
            self.max_history_token=llm_apikey_decrypt_service.cred_config.get('context',8096)
            # Retrieve max input tokens from the Hugging Face endpoint
            endpoint_information = self.llm_huggingface.client.get_endpoint_info()
            huggingface_context_token = endpoint_information['max_input_tokens']
            max_output_tokens = endpoint_information['max_total_tokens']
            tokens_difference = max_output_tokens - huggingface_context_token
            # Check if the context token from Hugging Face meets or exceeds the max history token limit
            if huggingface_context_token >= self.max_history_token:
                if tokens_difference >= CustomGptDocConfig.MAX_TOTAL_TOKENS:
                    self.llm_huggingface.max_new_tokens = tokens_difference
                    pass
                else:
                    error_code="max_total_token_insufficient"
                    error_content= f"Insufficient Max Number of Tokens: {max_output_tokens}.Minimum {CustomGptDocConfig.MAX_TOTAL_TOKENS}  Tokens difference is required between Max Number of Tokens:{max_output_tokens} and Max Input Length:{huggingface_context_token}"
                    content = HF_ERROR_MESSAGES_CONFIG.get(error_code, HF_ERROR_MESSAGES_CONFIG.get("common_response"))
                    # Log the error before raising the exception
                    
                    if error_code not in HF_ERROR_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "HFToolServiceOpenai.validate_token_limits"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "HFToolServiceOpenai.validate_token_limits"}})
                    thread_repo.initialization(self.thread_id, self.thread_model)
                    thread_repo.add_message_huggingface(error_code)
                    

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": error_content,
                            "data": content,
                            "platform":"HUGGING_FACE",
                            "error_code":error_code
                        }
                    )
            else:
                error_code="context_length_insufficient"
                error_content= f"Insufficient context length: {huggingface_context_token}/{self.max_history_token} tokens required for this platfrom"
                content = HF_ERROR_MESSAGES_CONFIG.get(error_code, HF_ERROR_MESSAGES_CONFIG.get("common_response"))
                # Log the error before raising the exception
                
                if error_code not in HF_ERROR_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.validate_token_limits"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.validate_token_limits"}})
                thread_repo.initialization(self.thread_id, self.thread_model)
                thread_repo.add_message_huggingface(error_code)
                

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": error_content,
                        "data": content,
                        "platform":"HUGGING_FACE",
                        "error_code":error_code
                    }
                )
        except HTTPException as e:
               raise e
        except Exception as e:
            logger.error(
                f"Failed to Validate Context Limits: {e}",
                extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.validate_context_limits"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Failed to initialize LLM: {e}")
        
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
                llm=self.llm_huggingface_non_stream,
                max_token_limit=llm_apikey_decrypt_service.extra_config.get('maxInputTokens',4096),
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.initialize_memory"}})
        
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
            chat_docs.initialization(file_id_list=self.file_ids,collection_name=chat_doc_collection)
            namespace_list = chat_docs.get_brain_id_list()
            self.vectorstore = qdrant_vector_store.get_lot_retiver_namespace(top_k=CustomGptDocConfig.TOP_K,tag_list=self.tag,namespace_list=namespace_list, query=query, companymodel=company_model_collection, company_id=company_apikey_id)
        except Exception as e:
            logger.error(
                f"Failed to load vector store: {e}",
                extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.load_vector_store"}}
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
                        "tags": {"method": "HFCustomGPTStreamingDocChatService.prompt_attach"},
                        "additional_prompt_id": additional_prompt_id,
                        "collection_name": collection_name})
                else:
                    self.additional_prompt = None
            else:
                self.additional_prompt = None
        except Exception as e:
            logger.error(
                f"Failed to prompt attach: {e}",
                extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.prompt_attach"}}
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
            user_agent_name=custom_gpt_repo.get_name()
            user_system_prompt=custom_gpt_repo.get_gpt_system_prompt()
            user_goals=custom_gpt_repo.get_gpt_goals()
            user_instructions=custom_gpt_repo.get_gpt_instructions()
            user_custom_prompt.initialization(user_agent_name=user_agent_name, \
                                              user_system_prompt=user_system_prompt,user_goals=user_goals,user_instructions=user_instructions)
            qa_prompt = user_custom_prompt.create_chat_prompt_doc(additional_prompt=self.additional_prompt)
            self.conversational_retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm_huggingface,
                retriever=self.vectorstore,
                chain_type="stuff",
                combine_docs_chain_kwargs={'prompt': qa_prompt},
                return_source_documents=False,
                memory=self.memory,
                condense_question_llm=self.llm_huggingface_non_stream,
                verbose=False,
                rephrase_question=False
            )
            self.inputs={"question": input_text}
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(
                f"Failed to create conversation: {e}",
                extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.create_conversation"}}
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
            cost = CostCalculator()

            async with  \
                    get_custom_huggingface_callback(llm_apikey_decrypt_service.model_name, cost=cost, thread_id=thread_id, collection_name=collection_name,**kwargs) as cb, \
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=collection_name,regenerated_flag=regenerated_flag,msgCredit=msgCredit,is_paid_user=is_paid_user) as mongo_handler:

                run = asyncio.create_task(self.conversational_retrieval_chain.arun(
                    self._get_inputs(),
                    callbacks=[mongo_handler]
                ))
                
                async for token in self.callback_handler.aiter():
                    data = token.encode("utf-8")
                    yield f"data: {data}\n\n",200
                    await asyncio.sleep(delay_chunk)
                    # yield f"data: {json.dumps(token)}\n\n",200
                await run
        
        # Handling errors from Hugging Face libraries
        except ValueError as e:
            logger.error(f"Hugging Face Value Error: {e}", extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.ValueError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_huggingface("value_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("value_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except RuntimeError as e:
            logger.error(f"Hugging Face Runtime Error: {e}", extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.RuntimeError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_huggingface("runtime_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("runtime_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except EntryNotFoundError as e:
            logger.error(f"Entry Not Found: {e}", extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.EntryNotFoundError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_huggingface("entry_not_found")
            content = HF_ERROR_MESSAGES_CONFIG.get("entry_not_found", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except BadRequestError as e:
            logger.error(f"Bad Request Error: {e}", extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.BadRequestError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_huggingface("bad_request_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("bad_request_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except HfHubHTTPError as e:
            logger.error(f"Hugging Face Hub HTTP Error: {e}", extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.HfHubHTTPError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_huggingface("hf_hub_http_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("hf_hub_http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": DEV_MESSAGES_CONFIG.get('hugging_face_message'), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except HTTPError as e:
            logger.error(f"Hugging Face HTTP Error: {e}", extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.HTTPError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_huggingface("http_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": DEV_MESSAGES_CONFIG.get('hugging_face_message'), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in HF_ERROR_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.Exception_Except"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.Exception_Except"}})
                thread_repo.initialization(self.thread_id, collection_name)
                thread_repo.add_message_huggingface(error_code)
                content = HF_ERROR_MESSAGES_CONFIG.get(error_code, HF_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.stream_run_conversation.Exception_Except"}})
                thread_repo.initialization(self.thread_id, collection_name)
                thread_repo.add_message_huggingface("common_response")
                content = HF_ERROR_MESSAGES_CONFIG.get("common_response")
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
                'callback_handler'
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
                    extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "HFCustomGPTStreamingDocChatService.cleanup"}}
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
