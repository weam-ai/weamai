from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.chains import LLMChain
from src.chatflow_langchain.service.openai.enhancement.chat_prompt_factory import chat_prompt_query_enhance
from bson import ObjectId
from langchain_community.callbacks.manager import get_openai_callback
from src.logger.default_logger import logger

## Custom Library Imports
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from fastapi import HTTPException, status
import gc
from src.chatflow_langchain.service.openai.title.utils import extract_error_message
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError,NotFoundError
from src.crypto_hub.utils.crypto_utils import crypto_service
from src.chatflow_langchain.service.config.model_config_openai import DefaultOpenAIModelRepository,OPENAIMODEL
from src.chatflow_langchain.repositories.enhacement import EnhanceRepostiory
from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_openai import Functionality
from dotenv import load_dotenv
import os
from datetime import datetime
import pytz
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()

class OpenAIQueryEnhancerService():
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

    async def initialize_input(self,chat_input:dict):
        """
        Initializes the language model with the given chat input.

        Args:
            chat_input (dict): A dictionary containing the input data for the chat.
        """
 
        self.enhance_repo=EnhanceRepostiory()
        self.chat_input=chat_input
        self.query_id=self.chat_input.query_id
        self.query=self.chat_input.query
        self.chat_id=self.chat_input.query_id # Changed from chat_id to query_id as its no longer needed
        self.brain_id=self.chat_input.brain_id
        self.user_id=self.chat_input.user_id
        self.api_usage_service = APIKeyUsageService()
        self.enhance_repo.initialization(query_id=self.query_id,\
                                               chat_id=self.chat_id,brain_id=self.chat_input.brain_id,collection_name=self.chat_input.collection_name)
        self.enhance_id=await self.enhance_repo.set_enhance_id()
     
       
    async def initialize_llm(self, api_key_id: str = None,companymodel: str = None):
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
      
            self.company_id=self.chat_input.company_id
            self.api_key_id=DefaultOpenAIModelRepository(company_id=self.company_id,companymodel=companymodel).get_default_model_key()
            llm_apikey_decrypt_service.initialization(self.api_key_id, companymodel)
            self.companyRedis_id = llm_apikey_decrypt_service.companyRedis_id
            self.llm = ChatOpenAI(
                model_name=llm_apikey_decrypt_service.model_name,
                temperature=1.0,
                max_tokens=1400,
                use_responses_api=True,
                api_key=llm_apikey_decrypt_service.decrypt())
            self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}",
                         extra={"tags": {"method": "OpenAIQueryEnhancerService.initialize_llm"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
    

    async def create_prompt(self):
        """
        Creates a conversation chain with a custom prompt.
        """
        try:
            self.prompt = chat_prompt_query_enhance()
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}",
                         extra={"tags": {"method": "OpenAIQueryEnhancerService.create_prompt"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create prompt: {e}")
    async def create_chain(self):
        """
        Sets up the conversation chain with the LLM and prompt, and initializes the output parser.
        """
        try:
            self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "OpenAIQueryEnhancerService.create_chain"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create chain: {e}")
        
    async def insert_enhance_query(self,enhance_response:str,cb=None):
        """
        Updates the chat session title in the repository.

        Parameters
        ----------
        chat_session_id : str
            The ID of the chat session.
        title : str
            The new title for the chat session.
        """
        timezone = pytz.timezone("Asia/Kolkata")  # Adjust timezone if needed
        current_datetime = datetime.now(timezone)
  
        current_max_version=await self.enhance_repo.fetch_max_version()

        data={
            "_id":ObjectId(self.enhance_id),
            "queryId": ObjectId(self.query_id),
            "versionNumber": (current_max_version+1),
            "query": crypto_service.encrypt(self.query),
            "enhancedContent": crypto_service.encrypt(enhance_response),
            "createdAt":current_datetime,
            "updatedAt": current_datetime,
            "chatId": ObjectId(self.chat_id),
            "brainId": ObjectId(self.brain_id),
            "userId": ObjectId(self.user_id),
            "companyId": ObjectId(self.company_id),
            "tokens": {
                "imageT": 0,
                "completion":cb.completion_tokens,
                "promptT": cb.prompt_tokens,
                "totalUsed": cb.total_tokens,
                "totalCost": f"${cb.total_cost}"
            },
            "model": {
                "title": "Open AI",
                "code": "OPEN_AI",
                "id": ObjectId(self.api_key_id)
            }
        }
        self.result_records=await self.enhance_repo.insert_new_record(data=data)
        
    async def run_chain(self):
        """
        Executes a conversation and updates the token usage and conversation history.

        Returns
        -------
        tuple
            A tuple containing the response and the callback data.
        """

        try:
           
            with get_openai_callback() as cb :
                response = await self.llm_chain.ainvoke({"question": self.query})
            # self.api_usage_service.update_usage_sync(provider=llm_apikey_decrypt_service.bot_data.get('code', 'OPEN_AI'), tokens_used=cb.total_tokens, model=llm_apikey_decrypt_service.model_name, api_key=llm_apikey_decrypt_service.apikey, functionality=Functionality.CHAT,company_id=self.companyRedis_id)
            await self.insert_enhance_query(enhance_response=response['text'],cb=cb)
            response = {
                "status": status.HTTP_200_OK,
                "message": "Successfully enhanced the query.",
                "data": response['text']
            }
            return response

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.NotFoundError"}})
            self.enhance_repo.add_message_openai(error_code)

            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))

            response = {
                "status": status.HTTP_417_EXPECTATION_FAILED,
                "message": error_content,
                "data": content
            }

            return response
        

        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.RateLimitError"}})
       
            self.enhance_repo.add_message_openai(error_code)
            
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))

            response = {
                "status": status.HTTP_417_EXPECTATION_FAILED,
                "message": error_content,
                "data": content
            }

            return response
   
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.APIStatusError"}})
               
                self.enhance_repo.add_message_openai("common_response")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "OpenAITitleGenerationService.run_chain.APIStatusError"}})
                self.enhance_repo.add_message_openai(error_code)
            
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))

            response = {
                "status": status.HTTP_417_EXPECTATION_FAILED,
                "message": error_content,
                "data": content
            }

            return response

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.LengthFinishReasonError"}})
            self.enhance_repo.add_message_openai("content_filter_issue")
            

            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))

            response = {
                "status": status.HTTP_417_EXPECTATION_FAILED,
                "message": e,
                "data": content
            }
            return response

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.ContentFilterFinishReasonError"}})
            
            self.enhance_repo.add_message_openai("content_filter_issue")
            
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))

            response = {
                "status": status.HTTP_417_EXPECTATION_FAILED,
                "message": e,
                "data": content
            }
            return response


        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.APITimeoutError"}})

            self.enhance_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))

            response = {
                "status": status.HTTP_417_EXPECTATION_FAILED,
                "message": e,
                "data": content
            }
            return response
        
        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "OpenAIQueryEnhancerService.run_chain.APIConnectionError"}})
            self.enhance_repo.add_message_openai("connection_error")

            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))

            response = {
                "status": status.HTTP_417_EXPECTATION_FAILED,
                "message": str(e),
                "data": content
            }
            return response

        except Exception as e:
                try:
                    error_content,error_code = extract_error_message(str(e))
                    if error_code not in OPENAI_MESSAGES_CONFIG:
                        logger.warning(
                            f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "OpenAIQueryEnhancerService.Exception_try"}})
                    else:
                        logger.error(
                            f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                            extra={"tags": {"method": "OpenAIQueryEnhancerService.Exception_try"}})
       
                    self.enhance_repo.add_message_openai(error_code)

                    content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
                    
                    response = {
                        "status": status.HTTP_417_EXPECTATION_FAILED,
                        "message": error_content,
                        "data": content
                    }
                    return response
                    
                except Exception as e:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {e}",
                        extra={"tags": {"method": "OpenAIQueryEnhancerService.Exception_Except"}})
                    self.enhance_repo.add_message_openai("common_response")

                    content = OPENAI_MESSAGES_CONFIG.get("common_response")
                    
                    response = {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": DEV_MESSAGES_CONFIG.get("dev_message"),
                        "data": content
                    }
                    return response
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
                    extra={"tags": {"method": "OpenAIQueryEnhancerService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "OpenAIQueryEnhancerService.cleanup"}}
            )