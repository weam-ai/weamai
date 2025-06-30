from fastapi import HTTPException,status
from src.logger.default_logger import logger
from src.chatflow_langchain.service.huggingface.title.title_generator import  HFTitleGenerationService,HFTitleImageGenerationService
from src.chatflow_langchain.service.openai.title.title_generator import OpenAITitleGenerationService
from src.chatflow_langchain.service.anthropic.title.title_generator import AnthropicTitleGenerationService
from src.chatflow_langchain.service.gemini.title.title_generator import GeminiTitleGenerationService
from src.chatflow_langchain.service.perplexity.title.title_generator import PerplexityTitleGenerationService
from src.gateway.exceptions import CustomTitleHttpException
from src.crypto_hub.services.huggingface.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.service.multimodal_router.title.title_generator import RouterTitleGenerationService
from src.chatflow_langchain.service.weam_router.deepseek.title.title_generator import WeamDeepSeekTitleGenerationService
from src.chatflow_langchain.service.weam_router.llama.title.title_generator import WeamLlamaTitleGenerationService
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
class TitleController:
    def __init__(self):
        self.managers = {
            "OPEN_AI": OpenAITitleGenerationService,
            "HUGGING_FACE": HFTitleGenerationService,
            "ANTHROPIC":AnthropicTitleGenerationService,
            "GEMINI":GeminiTitleGenerationService,
            "PERPLEXITY":PerplexityTitleGenerationService
        }
        self.huggingface_managers={
            "TEXT_GENERATION":HFTitleGenerationService,
            "IMAGE_GENERATION":HFTitleImageGenerationService
        }
        self.weam_router={
            "DEEPSEEK":RouterTitleGenerationService,
            "LLAMA4":RouterTitleGenerationService,
            "QWEN":RouterTitleGenerationService,
            "GROK":RouterTitleGenerationService
        }
     
        self.code = None  # Initialize the code attribute

    def initialization_service_code(self, code: str = None):
        """
        Initializes the Title with the specified API key and company model.

        Parameters
        ----------
        code : str, optional
            The API key ID used for decryption and initialization.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:
            self.code = code
            
        except Exception as e:
            logger.error(
                f"Failed to initialize Title Service: {e}",
                extra={"tags": {"method": "TitleController.initialization_service_code"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize Title Controller: {e}")
    
    def _select_manager(self, chat_input):
        """
        Selects the appropriate manager based on the code.
        """
        if self.code == "HUGGING_FACE":
            llm_apikey_decrypt_service.initialization(chat_input.llm_apikey, chat_input.companymodel)
            task_type = llm_apikey_decrypt_service.task_type
            return self.huggingface_managers.get(task_type, HFTitleImageGenerationService)()
        if chat_input.provider == "WEAM":
            return self.weam_router.get(self.code)()
        return self.managers.get(self.code)()


    async def service_hub_handler(self, chat_input,**kwargs):
        """
        Handles the Title input and returns the response.

        Parameters
        ----------
        chat_input : Any
            The input data for the chat.
        kwargs : Any
            Additional parameters.

        Returns
        -------
        response_generator : Any
            The response generator from the Title manager.
        """
        try:
            title_manager  = self._select_manager(chat_input)
            if title_manager is None:
                raise ValueError("Invalid Title code provided.")
            
            title_manager.initialize_llm(
            api_key_id=chat_input.llm_apikey,
            companymodel=chat_input.companymodel)

            title_manager.initialize_thread_data(chat_input.thread_id,collection_name=chat_input.threadmodel)
            title_manager.create_prompt()
            title_manager.create_chain()
            Title=''
            for title_response in title_manager.run_chain(chat_session_id=chat_input.chat_session_id,collection_name=chat_input.chatmodel,collection_chatmember=chat_input.chatmembermodel):
                if isinstance(title_response,str):
                    Title+=title_response
                else:
                    Title=title_response
                
            logger.info(
                "Successfully executed Generating title API",
                extra={"tags": {"endpoint": "/title-chat-generate"}}
            )
            return Title
            

        
        except HTTPException as he:
            logger.error(
                "HTTP error encountered during API request.",
                extra={"tags": {"endpoint": "/title-chat-generate", "chat_session_id": chat_input.chat_session_id, "error": str(he)}})

            raise CustomTitleHttpException(
                status_code=he.status_code,
                detail="Title generating was interrupted by an issue.",
                data={"chat_session_id":chat_input.chat_session_id,"chatmodel":chat_input.chatmodel,"chatmembermodel":chat_input.chatmembermodel})

        except Exception as e:
            logger.error(
                f"Failed to generate title and store text due to: {e}",
                extra={"tags": {"endpoint": "/title-chat-generation", "thread_id": chat_input.thread_id}})

            raise CustomTitleHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title generating was interrupted by an issue.",
                data={"chat_session_id":chat_input.chat_session_id,"chatmodel":chat_input.chatmodel,"chatmembermodel":chat_input.chatmembermodel})

