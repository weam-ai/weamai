import json
from langchain.chains import LLMChain
from src.chat.service.base.abstract_title_generation  import AbstractTitleGeneration
from src.chatflow_langchain.service.huggingface.title.chat_prompt_factory import create_chat_prompt_title
from src.chatflow_langchain.service.huggingface.title.chat_prompt_factory import prompt_title_without_answer
from src.chatflow_langchain.service.huggingface.title.custom_parser import TitleOutputParser
from src.custom_lib.langchain.callbacks.huggingface.cost.context_manager import get_huggingface_callback
from src.logger.default_logger import logger

## Custom Library Imports
from src.crypto_hub.services.huggingface.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.chat_session_repository import ChatSessionRepository
from src.chatflow_langchain.repositories.chat_member_repository import ChatMemberRepository
from fastapi import HTTPException, status
from src.chatflow_langchain.service.huggingface.title.config import REFORMED_QUERY
import gc
from src.chatflow_langchain.service.huggingface.title.utils import extract_error_message, get_default_title,get_default_image_title
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG, HF_ERROR_MESSAGES_CONFIG
from src.crypto_hub.utils.crypto_utils import MessageEncryptor,MessageDecryptor
from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from requests.exceptions import HTTPError
from huggingface_hub.utils import HfHubHTTPError, EntryNotFoundError, BadRequestError

llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
thread_repo = ThreadRepostiory()
chat_repo = ChatSessionRepository()
chat_member_repo = ChatMemberRepository()

load_dotenv()

key = os.getenv("SECURITY_KEY").encode("utf-8")

encryptor = MessageEncryptor(key)
decryptor = MessageDecryptor(key)


class HFTitleGenerationService(AbstractTitleGeneration):
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
            llm_apikey_decrypt_service.initialization(api_key_id, companymodel)
            self.task_type=llm_apikey_decrypt_service.task_type
         
            self.llm_huggingface_endpoint = HuggingFaceEndpoint(
                        endpoint_url=llm_apikey_decrypt_service.endpoint_url,
                        temperature=1.0,
                        repetition_penalty=2.0,
                        streaming=llm_apikey_decrypt_service.streaming,
                        huggingfacehub_api_token=llm_apikey_decrypt_service.decrypt(),
                        stop_sequences=llm_apikey_decrypt_service.extra_config.get('stopSequences',['<|eot_id|>']),
                        max_tokens=60
                    )
            self.llm_huggingface = ChatHuggingFace(llm=self.llm_huggingface_endpoint)
            self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}

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
                logger.error(f"Failed to initialize LLM: {e}",
                             extra={"tags": {"method": "HFTitleGenerationService.initialize_llm"}})
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
                         extra={"tags": {"method": "HFTitleGenerationService.initialize_thread_data"}})
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
                         extra={"tags": {"method": "HFTitleGenerationService.create_prompt"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create prompt: {e}")
    def create_chain(self):
        """
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        """
        try:
            self.llm_chain = LLMChain(llm=self.llm_huggingface, prompt=self.prompt, output_parser=TitleOutputParser())
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "HFTitleGenerationService.create_chain"}})
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
            with get_huggingface_callback() as cb :
                query = json.loads(decryptor.decrypt(thread_repo.result['message']))['data']['content']
                if self.ai_answer is None:
                    if len(query)>REFORMED_QUERY.QUERY_LIMIT_CHECK:
                        query=query[:REFORMED_QUERY.REFORMED_QUERY_LIMIT]
                    response = self.llm_chain.run({"question": query})
                else:
                    temp_ans = json.loads(decryptor.decrypt(self.ai_answer))['data']['content']
                    if (len(query)+len(temp_ans)) > REFORMED_QUERY.QUERY_LIMIT_CHECK:
                        reformed_query = query+temp_ans
                        reformed_query = reformed_query[:REFORMED_QUERY.REFORMED_QUERY_LIMIT]
                        response = self.llm_chain.run({"question": reformed_query,"answer":" "})
                    else:
                        response = self.llm_chain.run({"question": query, "answer": json.loads(decryptor.decrypt(self.ai_answer))['data']['content']})
                self.update_chat_session_title(chat_session_id, response,collection_name=collection_name)
                self.update_chat_member_title(chat_session_id,response,collection_name=collection_chatmember)

                tokens_old = thread_repo.result['tokens']
                
                self.update_token_usage(cb, tokens_old)

                yield response

        # Handling errors from Hugging Face libraries
        except ValueError as e:
            logger.error(f"Hugging Face Value Error: {e}", extra={"tags": {"method": "HFTitleGenerationService.run_chain.ValueError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("value_error")
            
            default_title = get_default_title("ValueError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)

            yield default_title

        except RuntimeError as e:
            logger.error(f"Hugging Face Runtime Error: {e}", extra={"tags": {"method": "HFTitleGenerationService.run_chain.RuntimeError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("runtime_error")
            
            default_title = get_default_title("RuntimeError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        # Hugging Face Hub Exceptions
        except EntryNotFoundError as e:
            logger.error(f"Entry Not Found: {e}", extra={"tags": {"method": "HFTitleGenerationService.run_chain.EntryNotFoundError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("entry_not_found")
            
            default_title = get_default_title("EntryNotFoundError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except BadRequestError as e:
            logger.error(f"Bad Request Error: {e}", extra={"tags": {"method": "HFTitleGenerationService.run_chain.BadRequestError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("bad_request_error")
            
            default_title = get_default_title("BadRequestError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title
        
        except HfHubHTTPError as e:
            logger.error(f"Hugging Face Hub HTTP Error: {e}", extra={"tags": {"method": "HFTitleGenerationService.run_chain.HfHubHTTPError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("hf_hub_http_error")
        
            default_title = get_default_title("HfHubHTTPError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except HTTPError as e:
            logger.error(f"Hugging Face HTTP Error: {e}", extra={"tags": {"method": "HFTitleGenerationService.run_chain.HTTPError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("http_error")
            
            default_title = get_default_title("HTTPError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title
        
        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in HF_ERROR_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFTitleGenerationService.run_chain.Exception_Except"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFTitleGenerationService.run_chain.Exception_Except"}})
                thread_repo.initialization(self.thread_id, self.thread_collection)
                thread_repo.add_message_huggingface(error_code)
                
                default_title = get_default_title("default")

                self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
                self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
                yield default_title

            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "HFTitleGenerationService.run_chain.Exception_Except"}})
                thread_repo.initialization(self.thread_id, self.thread_collection)
                thread_repo.add_message_huggingface("common_response")

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
                'ai_answer'
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
                    extra={"tags": {"method": "HFTitleGenerationService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "HFTitleGenerationService.cleanup"}}
            )





class HFTitleImageGenerationService(AbstractTitleGeneration):
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
            llm_apikey_decrypt_service.initialization(api_key_id, companymodel)
            self.task_type=llm_apikey_decrypt_service.task_type
            self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}

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
                logger.error(f"Failed to initialize LLM: {e}",
                             extra={"tags": {"method": "HFTitleImageGenerationService.initialize_llm"}})
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
                         extra={"tags": {"method": "HFTitleImageGenerationService.initialize_thread_data"}})
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
                         extra={"tags": {"method": "HFTitleImageGenerationService.create_prompt"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create prompt: {e}")
    def create_chain(self):
        """
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        """
        try:
            pass
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "HFTitleImageGenerationService.create_chain"}})
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
            
               
                response=get_default_image_title()
                self.update_chat_session_title(chat_session_id, response,collection_name=collection_name)
                self.update_chat_member_title(chat_session_id,response,collection_name=collection_chatmember)

                yield response

        # Handling errors from Hugging Face libraries
        except ValueError as e:
            logger.error(f"Hugging Face Value Error: {e}", extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.ValueError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("value_error")
            
            default_title = get_default_image_title("ValueError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)

            yield default_title

        except RuntimeError as e:
            logger.error(f"Hugging Face Runtime Error: {e}", extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.RuntimeError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("runtime_error")
            
            default_title = get_default_image_title("RuntimeError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        # Hugging Face Hub Exceptions
        except EntryNotFoundError as e:
            logger.error(f"Entry Not Found: {e}", extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.EntryNotFoundError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("entry_not_found")
            
            default_title = get_default_image_title("EntryNotFoundError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except BadRequestError as e:
            logger.error(f"Bad Request Error: {e}", extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.BadRequestError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("bad_request_error")
            
            default_title = get_default_image_title("BadRequestError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title
        
        except HfHubHTTPError as e:
            logger.error(f"Hugging Face Hub HTTP Error: {e}", extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.HfHubHTTPError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("hf_hub_http_error")
        
            default_title = get_default_image_title("HfHubHTTPError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title

        except HTTPError as e:
            logger.error(f"Hugging Face HTTP Error: {e}", extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.HTTPError"}})
            thread_repo.initialization(self.thread_id, self.thread_collection)
            thread_repo.add_message_huggingface("http_error")
            
            default_title = get_default_image_title("HTTPError")

            self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
            self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
            yield default_title
        
        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in HF_ERROR_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.Exception_Except"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.Exception_Except"}})
                thread_repo.initialization(self.thread_id, self.thread_collection)
                thread_repo.add_message_huggingface(error_code)
                
                default_title = get_default_image_title("default")

                self.update_chat_session_title(chat_session_id, default_title,collection_name=collection_name)
                self.update_chat_member_title(chat_session_id,default_title,collection_name=collection_chatmember)
                yield default_title

            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "HFTitleImageGenerationService.run_chain.Exception_Except"}})
                thread_repo.initialization(self.thread_id, self.thread_collection)
                thread_repo.add_message_huggingface("common_response")

                default_title = get_default_image_title("default")

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
                'prompt',
                'ai_answer'
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
                    extra={"tags": {"method": "HFTitleImageGenerationService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "HFTitleImageGenerationService.cleanup"}}
            )