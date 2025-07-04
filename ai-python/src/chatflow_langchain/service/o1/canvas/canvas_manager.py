import json
import asyncio
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationSummaryBufferMemory
from src.chatflow_langchain.service.o1.canvas.chat_prompt_factory import create_chat_prompt_canvas
from src.chatflow_langchain.service.o1.canvas.chat_prompt_factory import chat_prompt_with_code_canvas,chat_prompt_with_customgpt,chat_prompt_with_doc_canvas,chat_prompt_with_customgpt_doc
from langchain_community.callbacks.manager import get_openai_callback
from src.logger.default_logger import logger

## Custom Library Imports
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.langchain_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.vector_store.qdrant.langchain_lib.qdrant_store import QdrantVectorStoreService
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.custom_gpt_repository import CustomGPTRepository
from fastapi import HTTPException, status
from src.chatflow_langchain.service.o1.canvas.config import CanvasConfig,DEFAULTMODEL
from src.chatflow_langchain.service.config.model_config_openai import DefaultGPTTextModelRepository,OPENAIMODEL
import gc
from src.chatflow_langchain.service.o1.canvas.utils import extract_error_message,extract_languages,get_word_boundary_substring,regex_replace,regex_replace_v2
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError,NotFoundError
from src.crypto_hub.utils.crypto_utils import crypto_service
import os
from src.chatflow_langchain.repositories.chatdocs_repo import ChatDocsRepository
from src.chatflow_langchain.repositories.company_repository import CompanyRepostiory
from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_openai import Functionality
chat_docs = ChatDocsRepository()
company_repo=CompanyRepostiory()
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
new_thread_repo = ThreadRepostiory()
custom_gpt_repo=CustomGPTRepository()
qdrant_vector_store=QdrantVectorStoreService()

class O1OpenAICanvasService():
    """
    Concrete implementation of the AbstractConversationService for managing conversations.

    Methods
    -------
    initialize_llm(api_key_id: str = None, companymodel: str = None)
        Initializes the LLM (Language Learning Model) with the given API key and company model.
        
    initialize_thread_data(thread_id: str = None, collection_name: str = None)
        Initializes the chat history repository for data storage and sets up the memory component.
        
    create_prompt()
        Creates a conversation chain with a custom prompt.
        
    create_chain()
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        
    run_chain(chat_session_id: str = None, collection_name: str = None)
        Executes a conversation, updates the token usage, and stores the conversation history.
    """
    def extract_selected_text(self,start_index:int=0,end_index:int=None,user_query:str=None):
        """
        Creates a conversation chain with a custom prompt.
        """
        try:
            self.start_index=start_index
            self.user_query=user_query
            self.end_index=end_index
            self.ai_answer = thread_repo.result.get('ai',None)
            if self.ai_answer is None:
                self.ai_answer=thread_repo.result.get("openai_error")['content']
            else:
                self.ai_answer = json.loads(crypto_service.decrypt(self.ai_answer))['data']['content']
            if self.end_index is None:
                self.end_index=len(self.ai_answer)
            if self.regenerated_flag:
                self.user_query = " Regenerate the above response with improvements in clarity, relevance, and depth as needed. Adjust the level of detail based on the query's requirements—providing a concise response when appropriate and a more detailed, expanded answer when necessary." + self.user_query
                self.start_index=0
                self.end_index=len(self.ai_answer)
            self.selected_text_part,self.start_index,self.end_index = get_word_boundary_substring(text=self.ai_answer,start_index=self.start_index,end_index=self.end_index)
            self.extracted_code = extract_languages(self.ai_answer)
           
        except Exception as e:
            logger.error(f"Failed to extract selected text: {e}",
                         extra={"tags": {"method": "O1CanvasService.extract_selected_text"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to extract selected text: {e}")

    def initialize_llm(self, api_key_id: str = None, companymodel: str = None):
        """
        Initializes the LLM with the specified API key and company model.

        Parameters
        ----------
        api_key_id : str, optional
            The API key ID used for decryption and initialization.
        companymodel : str, optional
            The company model configuration for the LLM.
        """
        try:
            self.api_usage_service = APIKeyUsageService()
            self.tools = [regex_replace]
            llm_apikey_decrypt_service.initialization(api_key_id, companymodel)
            self.companyRedis_id=llm_apikey_decrypt_service.companyRedis_id
            self.model_name = OPENAIMODEL.MODEL_FOR_O1_CANVAS
            self.llm = ChatOpenAI(
                model_name=OPENAIMODEL.MODEL_FOR_O1_CANVAS,
                temperature=0.7,
                use_responses_api=True,
                api_key=llm_apikey_decrypt_service.decrypt()
            )
            self.llm_with_tools = self.llm.bind_tools(self.tools,tool_choice='required')
            self.llm_sum_memory = ChatOpenAI(
                model_name=OPENAIMODEL.MODEL_FOR_O1_CANVAS,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False,
                use_responses_api=True
            )
            self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}",
                         extra={"tags": {"method": "O1CanvasService.initialize_llm"}})
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
                max_token_limit=CanvasConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "O1CanvasService.initialize_memory"}}
            )

    def initialize_repository(self, chat_session_id: str = None, chat_collection_name: str = None):
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
                collection_name=chat_collection_name,
                regenerated_flag=self.regenerated_flag,
                thread_id=self.thread_id
            )
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "O1CanvasService.initialize_repository"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initalize repository: {e}")
    
    def initialize_thread_data(self, thread_id: str = None, collection_name: str = None,regenerated_flag:bool=False):
        """
        Initializes the chat history repository for data storage.

        Parameters
        ----------
        thread_id : str, optional
            The thread ID for the repository.
        collection_name : str, optional
            The collection name for the repository.
        """
        self.thread_id = thread_id
        try:
            thread_repo.initialization(thread_id, collection_name)
            self.api_type=thread_repo.get_api_type()
            self.regenerated_flag = regenerated_flag
        except Exception as e:
            logger.error(f"Failed to initialize thread data: {e}",
                         extra={"tags": {"method": "O1CanvasService.initialize_thread_data"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize thread data: {e}")
        
    def fetch_openai(self):
        try:
            self.initialize_llm(api_key_id= self.api_key_id,companymodel=self.company_model_collection)
            if len(self.extracted_code)>0:
                self.prompt_list  = chat_prompt_with_code_canvas()
            else:
                self.prompt_list = create_chat_prompt_canvas(general_user_template=f"context: {self.ai_answer}\nselected_text: {self.selected_text_part}\nQuery:{self.user_query}")
            self.query_arguments={"original_text":self.ai_answer}
        except Exception as e:
            logger.error(f"Error occurred during OpenAI fetching: {e}",extra={"tags": {"method": "O1CanvasService.fetch_openai"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to fetch response from OpenAI: {e}")
        
    def fetch_data_doc(self):
        try:
            # Fetch data from old_thread_repo
            self.initialize_llm(api_key_id= self.api_key_id,companymodel=self.company_model_collection)

            self.file_data = thread_repo.get_file_data()
            if isinstance(self.file_data,list):
                self.tag=[doc['uri'].split("/")[-1] for doc in self.file_data]
                self.file_ids = [str(doc['_id']) for doc in self.file_data]
                self.embedder_api_key_id = self.file_data[0].get('embedding_api_key',None)
            else:
                self.tag = [self.file_data['uri'].split("/")[-1]]
                self.file_ids = [str(self.file_data['_id'])]
                self.embedder_api_key_id = self.file_data.get('embedding_api_key',None)

            self.brain_data = thread_repo.get_brain_data()
            chat_docs.initialization(file_id_list=self.file_ids,collection_name=self.chat_doc_collection)
            namespace_list = chat_docs.get_brain_id_list()

            # Get embedding API key from file_data
            self.embedder_api_key_id = self.file_data.get('embedding_api_key',None)
            if self.embedder_api_key_id is None:
                embedder_model=DefaultGPTTextModelRepository(company_id=self.company_id,companymodel=self.company_model_collection)
                self.embedder_api_key_id=str(embedder_model.get_default_model_key())
            else:
                self.embedder_api_key_id=str(self.embedder_api_key_id)

            # Store inputs
            self.namespace = str(self.brain_data['id'])

            # Assuming self.company_id is available elsewhere in the class
            qdrant_vector_store.initialization(
                company_apikey_id=self.company_id,
                namespace=self.namespace,
                embedder_api_key_id=self.embedder_api_key_id,
                companypinecone_collection=self.companypinecone_collection,
                company_model_collection=self.company_model_collection,
                text_field=self.text_field,
            )
            
            # Get the initialized vector store
            self.vectorstore = qdrant_vector_store.get_lot_retiver_namespace(top_k=CanvasConfig.TOP_K,tag_list=self.tag,namespace_list=namespace_list, query=self.user_query, companymodel=self.company_model_collection, company_id=self.company_id)
            chunks=qdrant_vector_store.multi_doc_query(query_text=self.selected_text_part)
            

            self.prompt_list = chat_prompt_with_doc_canvas(general_user_template=f"context: {self.ai_answer}\nselected_text: {self.selected_text_part}\nQuery::{self.user_query}\nchunks:{chunks}")
            self.query_arguments={"original_text":self.ai_answer,'selected_text':self.selected_text_part,"chunks":chunks}
        except Exception as e:
            logger.error(f"Error occurred during data fetching: {e}",
                         extra={"tags": {"method": "O1CanvasService.fetch_data_doc"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to fetch data from thread repository: {e}")

    def fetch_data_custom_gpt_doc(self):
        try:
            # Fetch data from old_thread_repo
            self.custom_gpt_id=thread_repo.get_custom_gpt_id()
            custom_gpt_repo.initialization(custom_gpt_id=self.custom_gpt_id,collection_name=self.custom_gpt_collection)
            api_key_id=self.api_key_id


            self.initialize_llm(api_key_id= str(api_key_id),companymodel=self.company_model_collection)
            self.tag=custom_gpt_repo.get_gpt_file_tag_list()
            self.file_ids = custom_gpt_repo.get_gpt_file_ids()
            self.file_data = thread_repo.get_file_data()
            if isinstance(self.file_data,list):
                self.extra_tag = [doc['uri'].split("/")[-1] for doc in self.file_data if 'gptCoverImage' not in doc]
                self.extra_file_ids = [str(doc['_id']) for doc in self.file_data if 'gptCoverImage' not in doc]
            else:
                if 'gptCoverImage' not in self.file_data:
                    self.extra_tag = [self.file_data['uri'].split("/")[-1]]
                    self.extra_file_ids = [str(self.file_data['_id'])]
            self.file_ids += self.extra_file_ids
            self.tag += self.extra_tag
            user_agent_name=custom_gpt_repo.get_name()
            user_system_prompt=custom_gpt_repo.get_gpt_system_prompt()
            user_goals=custom_gpt_repo.get_gpt_goals()
            user_instructions=custom_gpt_repo.get_gpt_instructions()
            if custom_gpt_repo.get_doc_flag() or len(self.tag)>0:
                chat_docs.initialization(file_id_list=self.file_ids,collection_name=self.chat_doc_collection)
                namespace_list = chat_docs.get_brain_id_list()
                self.namespace = custom_gpt_repo.get_gpt_brain_id()
                self.embedder_api_key_id=custom_gpt_repo.get_gpt_embedding_key()

                if self.embedder_api_key_id is None or self.embedder_api_key_id=="None":
                    embedder_model=DefaultGPTTextModelRepository(company_id=self.company_id,companymodel=self.company_model_collection)
                    self.embedder_api_key_id=str(embedder_model.get_default_model_key())
                else:
                    self.embedder_api_key_id=str(self.embedder_api_key_id)
                    self.tag = custom_gpt_repo.get_gpt_file_tag()
        
                # Assuming self.company_id is available elsewhere in the class
                qdrant_vector_store.initialization(
                    company_apikey_id=self.company_id,
                    namespace=self.namespace,
                    embedder_api_key_id=self.embedder_api_key_id,
                    companypinecone_collection=self.companypinecone_collection,
                    company_model_collection=self.company_model_collection,
                    text_field=self.text_field,
                )

                # Get the initialized vector store
                self.vectorstore = qdrant_vector_store.get_lot_retiver_namespace(top_k=CanvasConfig.TOP_K,tag_list=self.tag,namespace_list=namespace_list, query=self.user_query, companymodel=self.company_model_collection, company_id=self.company_id)
                chunks=qdrant_vector_store.multi_doc_query(query_text=self.selected_text_part)
                self.query_arguments={"original_text":self.ai_answer,'selected_text':self.selected_text_part,
                                    "chunks":chunks,"user_agent_name":user_agent_name,"user_system_prompt":user_system_prompt,
                                    "user_goals":user_goals,"user_instructions":user_instructions}
                
                user_template_string=f"""
                                        Context: {self.ai_answer}
                                        Selected Text: {self.selected_text_part}
                                        Query: {self.user_query}

                                        # User Agent Information
                                        User Agent Name: {user_agent_name}
                                        System Prompt: {user_system_prompt}
                                        Goals: {user_goals}
                                        Instructions: {user_instructions}

                                        # Additional Chunks Information
                                        Chunks: {chunks}
                                    """
                
                self.prompt_list = chat_prompt_with_customgpt_doc(general_ai_template=user_template_string)
            else:
                user_template_string=f"""
                                        Context: {self.ai_answer}
                                        Selected Text: {self.selected_text_part}
                                        Query: {self.user_query}

                                        # User Agent Information
                                        User Agent Name: {user_agent_name}
                                        System Prompt: {user_system_prompt}
                                        Goals: {user_goals}
                                        Instructions: {user_instructions}
                                    """
           
                self.prompt_list = chat_prompt_with_customgpt(general_user_template=user_template_string)
                self.query_arguments={"original_text":self.ai_answer,'selected_text':self.selected_text_part,
                            "user_agent_name":user_agent_name,"user_system_prompt":user_system_prompt,
                            "user_goals":user_goals,"user_instructions":user_instructions}
        except Exception as e:
            logger.error(f"Error occurred during data fetching of custom gpt with doc: {e}",extra={"tags": {"method": "O1CanvasService.fetch_data_custom_gpt_doc"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to fetch data of custom gpt with doc: {e}")

    def fetch_data(self,api_key_id:str=None,company_id:str=None,companypinecone_collection: str=None, companymodel: str=None, custom_gpt_collection:str=None,text_field: str='text',chat_doc_collection:str="chatdocs"):
        # Define the different API types and their associated methods
        # Initialize an empty dictionary for data fetch methods
        try:
            self.chat_doc_collection = chat_doc_collection
            self.data_fetch_methods = {
                CanvasConfig.OPEN_AI_WITH_DOC: self.fetch_data_doc,
                CanvasConfig.OPEN_AI: self.fetch_openai,
                CanvasConfig.PERPLEXITY: self.fetch_openai,
                CanvasConfig.CUSTOM_GPT:self.fetch_data_custom_gpt_doc,
                CanvasConfig.OPEN_AI_CHAT_CANVAS:self.fetch_openai}
            
            self.companypinecone_collection=companypinecone_collection
            self.company_model_collection=companymodel
            self.text_field=text_field
            self.custom_gpt_collection=custom_gpt_collection
            self.api_key_id=api_key_id
            self.company_id=company_id
            # Execute the method based on the current API type
            self.data_fetch_methods[self.api_type]()
        except Exception as e:
            logger.error(f"Error occurred during data fetching: {e}",extra={"tags": {"method": "O1CanvasService.fetch_data"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to fetch data: {e}")

    def create_chain(self):
        """
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        """
        try:
            if len(self.extracted_code)>0:
                self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_list)
            pass
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "O1CanvasService.create_chain"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create chain: {e}")    
    def update_token_usage(self, cb, tokens_old):
        """
        Updates the token usage data in the repository.

        Parameters
        ----------
        cb : Callback
            The callback object containing token usage information.
        tokens_old : dict
            The old token usage data.
        """
        if 'totalCost' not in tokens_old:
            tokens_old = self.default_token_dict
        total_old_cost = float(tokens_old['totalCost'].replace("$", ""))
        total_new_cost = total_old_cost + cb.total_cost

        token_data = {
            "$set": {
                "tokens.totalUsed": tokens_old['totalUsed'] + cb.total_tokens,
                "tokens.promptT": tokens_old['promptT'] + cb.prompt_tokens,
                "tokens.completion": tokens_old['completion'] + cb.completion_tokens,
                "tokens.totalCost": f"${total_new_cost}"
            }
        }
        new_thread_repo.update_token_fields(token_data)
    
       # Separate async function to handle repository updates and history logging
    async def async_initialize_and_update(self, chat_session_id, chat_collection_name, new_thread_id, collection_name, cb, final_answer,msgCredit,is_paid_user):
        try:
            new_thread_repo.initialization(thread_id=new_thread_id, collection_name=collection_name)       

            # thread token update
            tokens_old = new_thread_repo.result['tokens']
            self.update_token_usage(cb, tokens_old)

            # Initialize the repositories
            self.initialize_repository(chat_session_id=chat_session_id, chat_collection_name=chat_collection_name)
            self.chat_repository_history.add_ai_message(
                message=final_answer,
                thread_id=new_thread_id)
            
            # Use callback to prune memory
            with get_openai_callback() as summary_cb:
                self.memory.prune()
            # await self.api_usage_service.update_usage(provider=llm_apikey_decrypt_service.bot_data.get('code', 'OPEN_AI'),tokens_used= summary_cb.total_tokens, model=self.model_name, api_key=llm_apikey_decrypt_service.apikey,functionality=Functionality.CHAT,company_id=self.companyRedis_id)

            # Add system message to chat history
            self.chat_repository_history.add_message_system(
                message=self.memory.moving_summary_buffer,
                thread_id=new_thread_id)
            
            # Update token usage summary
            new_thread_repo.update_token_usage_summary(cb=summary_cb)
            if is_paid_user:
                new_thread_repo.update_credits(msgCredit=msgCredit)
            else:
                company_repo.initialization(company_id=str(new_thread_repo.result['companyId']),collection_name='company')
                company_repo.update_free_messages(model_code='OPEN_AI')
            logger.info("Database successfully stored response",
                extra={"tags":{"method": "CanavasGenerationService.async_initialize_and_update"}})
        except Exception as e:
            logger.error(f"Error occurred during async initialization and update: {e}",
                         extra={"tags": {"method": "O1CanvasService.async_initialize_and_update"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to initialize and update chat thread: {e}")

    async def run_chain(self, query:str=None,new_thread_id:str=None,chat_session_id: str = None, chat_collection_name: str = None,collection_name:str=None,delay_chunk:int=0,msgCredit:float=0,is_paid_user:bool=False):
        """
        Executes a conversation and updates the token usage and conversation history.

        Returns
        -------
        tuple
            A tuple containing the response and the callback data.
        """
        try:
            if query =='Ask Weam':
                query = 'Enhance This'
            self.query_arguments.update({'query':query})
            with get_openai_callback() as cb :
                    if len(self.extracted_code)>0:
                        response = self.llm_chain.run(self.query_arguments)
                        final_answer=response
                    else:
                        response = self.llm_with_tools.invoke(self.prompt_list)
                        tool_call = response.tool_calls

                        final_answer = self.ai_answer  # Start with the initial answer

                        # Loop through each tool call
                        for call in tool_call:
                            regex_pattern = call['args']['regex_pattern']
                            replacement_string = call['args']['replacement_string']
                            # Perform the regex replacement and update final_answer
                            final_answer = regex_replace_v2(
                                regex_pattern=regex_pattern, 
                                replacement_string=replacement_string,
                                original_string=final_answer  # Use the updated answer as original string
                            )

            # await self.api_usage_service.update_usage(provider=llm_apikey_decrypt_service.bot_data.get('code', 'OPEN_AI'),tokens_used= cb.total_tokens, model=self.model_name, api_key=llm_apikey_decrypt_service.apikey,functionality=Functionality.CHAT,company_id=self.companyRedis_id)
            # Define a task to run async initialization and update concurrently
            update_task = asyncio.create_task(
                self.async_initialize_and_update(chat_session_id, chat_collection_name, 
                                                new_thread_id, collection_name, cb, final_answer,msgCredit,is_paid_user))
            try:
            # Stream the final answer in chunks while updates run in parallel
                chunk_size = 5  # Adjust the size of each streamed chunk
                for i in range(0, len(final_answer), chunk_size):
                    token = final_answer[i:i + chunk_size]
                    # Yield each chunk of the final answer with HTTP 200 status
                    token = token.encode("utf-8")
                    yield f"data: {token}\n\n", 200
                    # Add a small delay to simulate streaming and avoid blocking
                    await asyncio.sleep(delay_chunk)
        
            finally:
            # Ensure the update task completes regardless of success or failure in streaming
                await update_task

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CanvasService.run_chain.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CanvasService.run_chain.NotFoundError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_openai(error_code)

            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CanvasService.run_chain.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CanvasService.run_chain.RateLimitError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
   
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CanvasService.run_chain.APIStatusError"}})
                thread_repo.initialization(self.thread_id, collection_name)
                thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "O1CanvasService.run_chain.APIStatusError"}})
                thread_repo.initialization(self.thread_id, collection_name)
                thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "O1CanvasService.run_chain.LengthFinishReasonError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "O1CanvasService.run_chain.ContentFilterFinishReasonError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "O1CanvasService.run_chain.APITimeoutError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "O1CanvasService.run_chain.APIConnectionError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in OPENAI_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "O1CanvasService.run_chain.Exception_Except"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "O1CanvasService.run_chain.Exception_Except"}})
                    thread_repo.initialization(self.thread_id, collection_name)
                    thread_repo.add_message_openai(error_code)
                    content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
                    yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
                except Exception as e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "O1CanvasService.run_chain.Exception_Except"}})
                    thread_repo.initialization(self.thread_id, collection_name)
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
                'llm_chain',
                'llm_sum_memory',
                'memory',
                'chat_repository_history',
                'prompt',
                'ai_answer',
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
                    extra={"tags": {"method": "O1CanvasService.cleanup"}})

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "O1CanvasService.cleanup"}})