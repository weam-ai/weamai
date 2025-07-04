import json
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.chains import LLMChain
from src.chat.service.base.abstract_title_generation  import AbstractTitleGeneration
from src.chatflow_langchain.service.o1.title.chat_prompt_factory import create_chat_prompt_title
from src.chatflow_langchain.service.o1.title.chat_prompt_factory import prompt_title_without_answer
from src.chatflow_langchain.service.o1.title.custom_parser import TitleOutputParser
from langchain_community.callbacks.manager import get_openai_callback
from src.logger.default_logger import logger

## Custom Library Imports
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.chat_session_repository import ChatSessionRepository
from src.chatflow_langchain.repositories.chat_member_repository import ChatMemberRepository
from fastapi import HTTPException, status
from src.chatflow_langchain.service.o1.title.config import REFORMED_QUERY
from src.chatflow_langchain.service.config.model_config_openai import OPENAIMODEL
import gc
from src.chatflow_langchain.service.o1.title.utils import extract_error_message, get_default_title
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError,NotFoundError
from src.crypto_hub.utils.crypto_utils import crypto_service
import os
from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_openai import Functionality

llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
chat_repo = ChatSessionRepository()
chat_member_repo = ChatMemberRepository()

class OpenAITitleGenerationService(AbstractTitleGeneration):
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
            llm_apikey_decrypt_service.initialization(api_key_id, companymodel)
            self.companyRedis_id=llm_apikey_decrypt_service.companyRedis_id
            self.llm = ChatOpenAI(
                model_name=OPENAIMODEL.GPT_4_1_MINI,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature', 0.7),
                api_key=llm_apikey_decrypt_service.decrypt(),
                use_responses_api=True,
                max_tokens=35
            )
            self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}",
                         extra={"tags": {"method": "OpenAITitleGenerationService.initialize_llm"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
    
    def initialize_thread_data(self, thread_id: str = None, collection_name: str = None):
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
        self.thread_collection=collection_name
        try:
            thread_repo.initialization(thread_id, collection_name)
        except Exception as e:
            logger.error(f"Failed to initialize thread data: {e}",
                         extra={"tags": {"method": "OpenAITitleGenerationService.initialize_thread_data"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize thread data: {e}")
    def create_prompt(self):
        """
        Creates a conversation chain with a custom prompt.
        """
        try:
            self.ai_answer = thread_repo.result.get('ai',None)
            if self.ai_answer is None:
                self.prompt = prompt_title_without_answer()
            else:
                self.prompt = create_chat_prompt_title()
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}",
                         extra={"tags": {"method": "OpenAITitleGenerationService.create_prompt"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create prompt: {e}")
    def create_chain(self):
        """
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        """
        try:
            self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt, output_parser=TitleOutputParser())
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "OpenAITitleGenerationService.create_chain"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create chain: {e}")
        
    def update_chat_session_title(self, chat_session_id: str=None, title: str=None,collection_name:str=None):
        """
        Updates the chat session title in the repository.

        Parameters
        ----------
        chat_session_id : str
            The ID of the chat session.
        title : str
            The new title for the chat session.
        """
        chat_repo.initialization(chat_session_id=chat_session_id,collection_name=collection_name)
        title_data = {"$set": {"title": title}}
        chat_repo.update_fields(data=title_data)
    
    def update_chat_member_title(self, chat_session_id: str=None, title: str=None,collection_name:str=None):
        """
        Updates the chat session title in the repository.

        Parameters
        ----------
        chat_session_id : str
            The ID of the chat session.
        title : str
            The new title for the chat session.
        """
        chat_member_repo.initialization(chat_session_id=chat_session_id,collection_name=collection_name)
        title_data = {"$set": {"title": title}}
        chat_member_repo.update_title(data=title_data)       

   

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
        thread_repo.update_token_fields(token_data)

    def run_chain(self, chat_session_id: str = None, collection_name: str = None, collection_chatmember: str = None):
        """
        Executes a conversation and updates the token usage and conversation history.

        Returns
        -------
        tuple
            A tuple containing the response and the callback data.
        """
        try:
            with get_openai_callback() as cb :
                query = json.loads(crypto_service.decrypt(thread_repo.result['message']))['data']['content']
                if self.ai_answer is None:
                    if len(query)>REFORMED_QUERY.QUERY_LIMIT_CHECK:
                        query=query[:REFORMED_QUERY.REFORMED_QUERY_LIMIT]
                    response = self.llm_chain.run({"question": query})
                else:
                    temp_ans = json.loads(crypto_service.decrypt(self.ai_answer))['data']['content']
                    if (len(query)+len(temp_ans)) > REFORMED_QUERY.QUERY_LIMIT_CHECK:
                        reformed_query = query+temp_ans
                        reformed_query = reformed_query[:REFORMED_QUERY.REFORMED_QUERY_LIMIT]
                        response = self.llm_chain.run({"question": reformed_query,"answer":" "})
                    else:
                        response = self.llm_chain.run({"question": query, "answer": json.loads(crypto_service.decrypt(self.ai_answer))['data']['content']})
                    # self.api_usage_service.update_usage_sync(provider=llm_apikey_decrypt_service.bot_data.get('code', 'OPEN_AI'), tokens_used=cb.total_tokens, model=OPENAIMODEL.GPT_4_1_MINI, api_key=llm_apikey_decrypt_service.apikey, functionality=Functionality.CHAT,company_id=self.companyRedis_id)
                self.update_chat_session_title(chat_session_id, response,collection_name=collection_name)
                self.update_chat_member_title(chat_session_id,response,collection_name=collection_chatmember)

                tokens_old = thread_repo.result['tokens']
                
                self.update_token_usage(cb, tokens_old)

                yield response

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.NotFoundError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_openai(error_code)

            default_title = get_default_title("NotFoundError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)

            llm_apikey_decrypt_service.update_deprecated_status(True)
            yield default_title

        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.RateLimitError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_openai(error_code)
            
            default_title = get_default_title("RateLimitError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title
   
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.APIStatusError"}})
                thread_repo.initialization(self.thread_id, self.thread_collection)
                thread_repo.add_message_openai("common_response")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.APIStatusError"}})
                thread_repo.initialization(self.thread_id, self.thread_collection)
                thread_repo.add_message_openai(error_code)
            
            default_title = get_default_title("APIStatusError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.LengthFinishReasonError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_openai("content_filter_issue")
            
            default_title = get_default_title("LengthFinishReasonError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.ContentFilterFinishReasonError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_openai("content_filter_issue")
            
            default_title = get_default_title("ContentFilterFinishReasonError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.APITimeoutError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_openai("request_time_out")
            
            default_title = get_default_title("APITimeoutError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title
        
        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.APIConnectionError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_openai("connection_error")
            
            default_title = get_default_title("APIConnectionError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in OPENAI_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.Exception_Except"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.Exception_Except"}})
                    thread_repo.initialization(self.thread_id, self.thread_collection)
                    thread_repo.add_message_openai(error_code)

                    default_title = get_default_title("default")

                    self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
                    self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
                    yield default_title
                
                except Exception as e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.Exception_Except"}})
                    thread_repo.initialization(self.thread_id, self.thread_collection)
                    thread_repo.add_message_openai("common_response")
                    
                    default_title = get_default_title("default")

                    self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
                    self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
                    yield default_title
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
                    extra={"tags": {"method": "OpenAITitleGenerationService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "OpenAITitleGenerationService.cleanup"}}
            )