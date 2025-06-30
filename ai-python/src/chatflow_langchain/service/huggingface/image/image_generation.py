import json 
import asyncio
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.callbacks.manager import get_openai_callback
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from src.chatflow_langchain.utils.upload_image import upload_image_to_s3,generate_random_file_name
from src.chatflow_langchain.service.huggingface.image.chat_prompt_factory import ImagePrompt
from src.custom_lib.langchain.chain.custom_conversation_chain import CustomConversationChain
from src.crypto_hub.services.huggingface.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.langchain_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.logger.default_logger import logger
from fastapi import HTTPException,status
## Custom Library 
from src.custom_lib.langchain.callbacks.openai.image_cost.dalle_cost import CostCalculator
from src.custom_lib.langchain.callbacks.openai.image_cost.context_manager import dalle_callback_handler
from src.chatflow_langchain.service.huggingface.image.config import ImageGenerateConfig

#Abstract library
from src.chat.repositories.abstract_image_generation_repository import ImageGenerationAbstractRepository
from src.chatflow_langchain.service.huggingface.image.utils import extract_error_message
import gc
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG,HF_ERROR_MESSAGES_CONFIG
from src.chatflow_langchain.utils.fill_additional_prompt import fill_template, format_website_summary_pairs
from requests.exceptions import HTTPError
from huggingface_hub.utils import HfHubHTTPError, EntryNotFoundError, BadRequestError

# Service Initilization 
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
chat_repository_history = CustomAIMongoDBChatMessageHistory()
thread_repo = ThreadRepostiory()
prompt_repo = PromptRepository()
img_prompt = ImagePrompt()

class HFImageGenerationService(ImageGenerationAbstractRepository):
    """
    Concrete implementation of the AbstractConversationService for managing conversations.

    Methods
    -------
    initialize_llm(api_key_id: str = None, companymodel: str = None)
        Initializes the LLM (Language Learning Model) with the given API key and company model.
        
    initialize_repository(chat_session_id: str = None, collection_name: str = None)
        Initializes the chat history repository for data storage and sets up the memory component.
        
    initialize_memory()
        Sets up the memory component using ConversationSummaryBufferMemory.
        
    create_conversation(additional_prompt: str = "make the we defined response response")
        Creates a conversation chain with a custom prompt and initializes it with the LLM and memory.
        
    run_conversation(input_text: str, thread_id: str, collection_name: str)
        Executes a conversation with the given input text, updates the token usage, and stores the conversation history.
    """
    def initialize_llm_tool(self, api_key_id: str = None, companymodel: str = None,dalle_wrapper_size:str=None,dalle_wrapper_quality:str=None,dalle_wrapper_style:str=None):
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
            self.image_style = dalle_wrapper_style
            self.image_size = dalle_wrapper_size
            self.image_quality = dalle_wrapper_quality
            self.llm_model_name=ImageGenerateConfig.LLM_MODEL_NAME
            self.llm_image_name=llm_apikey_decrypt_service.model_name
            # self.llm_image_name = ImageGenerateConfig.LLM_IMAGE_NAME
            self.dalle_wrapper = DallEAPIWrapper(model=self.llm_image_name,api_key=llm_apikey_decrypt_service.decrypt(), \
                                                 n=1,quality=self.image_quality,size=self.image_size,style=self.image_style)
           
            self.llm_model= ChatOpenAI(
                model_name=self.llm_model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature',0.0),
                api_key=llm_apikey_decrypt_service.decrypt(),
                use_responses_api=True

            )
            self.dalle_generational_tool = OpenAIDALLEImageGenerationTool(api_wrapper=self.dalle_wrapper,verbose=False)
        except Exception as e:
            logger.error(
                f"Failed to initalize llm: {e}",
                extra={"tags": {"method": "HFImageGenerationService.initialize_llm_tool"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
        

    def initialize_repository(self, chat_session_id: str = None, collection_name: str = None):
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
            self.chat_repository_history = chat_repository_history.initialize(
                chat_session_id=chat_session_id,
                collection_name=collection_name
            )
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "HFImageGenerationService.initialize_repository"}}
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
                memory_key="history",
                input_key="input",
                llm=self.llm_model,
                max_token_limit=ImageGenerateConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=chat_repository_history
            )
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "HFImageGenerationService.initialize_memory"}}
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
                resource_key, resource_value = prompt_repo.get_resource_info()
                if resource_key is not None and resource_value is not None:
                    self.additional_prompt = fill_template(resource_key, resource_value)
                    websites = prompt_repo.get_websites()    
                    summaries = prompt_repo.get_summaries()  
                    formatted_pairs = format_website_summary_pairs(websites,summaries)
                    self.additional_prompt += formatted_pairs
                    logger.info("Successfully attached additional prompt", extra={
                        "tags": {"method": "HFImageGenerationService.prompt_attach"},
                        "additional_prompt_id": additional_prompt_id,
                        "collection_name": collection_name})
            else:
                self.additional_prompt = None
        except Exception as e:
            logger.error(
                f"Failed to prompt attach: {e}",
                extra={"tags": {"method": "HFImageGenerationService.prompt_attach"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to prompt attach: {e}")


    def create_conversation(self, input_text:str=None,**kwargs):
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
            img_prompt.initialization()
            self.prompt = img_prompt.create_chat_prompt_image(additional_prompt=self.additional_prompt,**kwargs)
            self.inputs={"input": input_text}
            self.conversation = CustomConversationChain(
            prompt=self.prompt,
            llm=self.llm_model,
            memory=self.memory,
            verbose=False)
        except Exception as e:
            logger.error(
                f"Failed to create conversation: {e}",
                extra={"tags": {"method": "HFImageGenerationService.create_conversation"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create conversation: {e}")
    def _get_inputs(self):
        return self.inputs
    
    def save_image_to_db(self,s3_file_name,thread_id,collection_name):
            thread_repo.initialization(thread_id=thread_id,collection_name=collection_name)
            chat_repository_history.add_ai_message(
                message=s3_file_name,
                thread_id=thread_id
            )
            with get_openai_callback() as cb:
                    self.memory.prune()
            
            thread_repo.update_token_usage_summary(cb)
            chat_repository_history.add_message_system(
                message=self.memory.moving_summary_buffer,
                thread_id=thread_id
            )

    async def run_image_generation(self,thread_id: str, collection_name: str,**kwargs):
        try:
            cost=CostCalculator()
            async with dalle_callback_handler(llm_model=self.llm_model_name, cost = cost,dalle_model=self.llm_image_name,thread_id=thread_id,collection_name=collection_name,image_quality = self.image_quality,image_size=self.image_size,image_style=self.image_style) as asynchandler:
                response = self.dalle_generational_tool.run(self.conversation.run(self._get_inputs(),callbacks=[asynchandler]),callbacks=[asynchandler])
                s3_file_name=generate_random_file_name()
                upload_image_to_s3(image_url=response,s3_file_name=s3_file_name)
                self.save_image_to_db(s3_file_name,thread_id,collection_name)
                yield json.dumps({"status": status.HTTP_200_OK, "message": s3_file_name}),status.HTTP_200_OK
                
        # Handling errors from Hugging Face libraries
        except ValueError as e:
            logger.error(f"Hugging Face Value Error: {e}", extra={"tags": {"method": "HFImageGenerationService.run_image_generation.ValueError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_huggingface("value_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("value_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except RuntimeError as e:
            logger.error(f"Hugging Face Runtime Error: {e}", extra={"tags": {"method": "HFImageGenerationService.run_image_generation.RuntimeError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_huggingface("runtime_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("runtime_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        # Hugging Face Hub Exceptions
        except EntryNotFoundError as e:
            logger.error(f"Entry Not Found: {e}", extra={"tags": {"method": "HFImageGenerationService.run_image_generation.EntryNotFoundError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_huggingface("entry_not_found")
            content = HF_ERROR_MESSAGES_CONFIG.get("entry_not_found", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except BadRequestError as e:
            logger.error(f"Bad Request Error: {e}", extra={"tags": {"method": "HFImageGenerationService.run_image_generation.BadRequestError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_huggingface("bad_request_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("bad_request_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except HfHubHTTPError as e:
            logger.error(f"Hugging Face Hub HTTP Error: {e}", extra={"tags": {"method": "HFImageGenerationService.run_image_generation.HfHubHTTPError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_huggingface("hf_hub_http_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("hf_hub_http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": DEV_MESSAGES_CONFIG.get('hugging_face_message'), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except HTTPError as e:
            logger.error(f"Hugging Face HTTP Error: {e}", extra={"tags": {"method": "HFImageGenerationService.run_image_generation.HTTPError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_huggingface("http_error")
            content = HF_ERROR_MESSAGES_CONFIG.get("http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": DEV_MESSAGES_CONFIG.get('hugging_face_message'), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in HF_ERROR_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFImageGenerationService.run_image_generation.Exception_Except"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "HFImageGenerationService.run_image_generation.Exception_Except"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_huggingface(error_code)
                content = HF_ERROR_MESSAGES_CONFIG.get(error_code, HF_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "HFImageGenerationService.run_image_generation.Exception_Except"}})
                thread_repo.initialization(self.thread_id, collection_name)
                thread_repo.add_message_huggingface("common_response")
                content = HF_ERROR_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

        finally:
            self.cleanup()

    def cleanup(self):
        """
        Cleans up any resources or state associated with the ImageGenerationService.
        """
        cleaned_up = []
        try:
            # List of attributes to clean up
            attributes = [
                'llm_model',
                'llm_image_name',
                'dalle_wrapper',
                'dalle_generational_tool',
                'memory',
                'conversation',
                'additional_prompt',
                'prompt'
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
                    extra={"tags": {"method": "HFImageGenerationService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "HFImageGenerationService.cleanup"}}
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