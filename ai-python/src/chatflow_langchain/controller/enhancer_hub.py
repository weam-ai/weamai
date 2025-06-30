from fastapi import HTTPException
from src.logger.default_logger import logger
from src.chatflow_langchain.service.openai.enhancement.enhancer import OpenAIQueryEnhancerService
from src.crypto_hub.services.huggingface.llm_api_key_decryption import LLMAPIKeyDecryptionHandler

llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
class EnhanceController:
    def __init__(self):
        self.managers = {
            "OPEN_AI": OpenAIQueryEnhancerService,
           
        }
        self.huggingface_managers={
            "TEXT_GENERATION":"HFEnhancerGenerationService",
            "IMAGE_GENERATION":"HFEnhancerGenerationService"
        }
        self.weam_router={
            ("DEEPSEEK","deepseek/deepseek-r1-distill-llama-70b"):"WeamDeepSeekEnhancerGenerationService",
            ("DEEPSEEK","deepseek/deepseek-r1"):"WeamDeepSeekEnhancerGenerationService",
            ("DEEPSEEK","deepseek/deepseek-r1-distill-qwen-32b"):"WeamDeepSeekEnhancerGenerationService",
            ("DEEPSEEK","deepseek/deepseek-r1:free"):"WeamDeepSeekEnhancerGenerationService",
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
                extra={"tags": {"method": "EnhanceController.initialization_service_code"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize Title Controller: {e}")
    
    def _select_manager(self, chat_input):
        """
        Selects the appropriate manager based on the code.
        """
        if self.code == "HUGGING_FACE":
            llm_apikey_decrypt_service.initialization(chat_input.llm_apikey, chat_input.companymodel)
            task_type = llm_apikey_decrypt_service.task_type
            return self.huggingface_managers.get(task_type, '')()
        if chat_input.provider == "WEAM":
            return self.weam_router.get((chat_input.code,chat_input.model_name))()
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
            The enhance response generator from the EnhanceController manager.
        """
        try:
            enhance_manager  = self._select_manager(chat_input)
            if enhance_manager is None:
                raise ValueError("Invalid Enhancer code provided.")
            await enhance_manager.initialize_input(chat_input=chat_input)
            await enhance_manager.initialize_llm(
            api_key_id=chat_input.llm_apikey,
            companymodel=chat_input.companymodel)
            await enhance_manager.create_prompt()
            await enhance_manager.create_chain()
          
            enhance_response=await enhance_manager.run_chain()
    
                
            logger.info(
                "Successfully executed Enhance Response",
                extra={"tags": {"endpoint": "/enhance-response-generation"}}
            )
            return enhance_response
            

        
        except HTTPException as he:
            logger.error(
                "HTTP error encountered during API request.",
                extra={"tags": {"endpoint": "/enhance-response-generation", "chat_session_id": chat_input.chat_id, "error": str(he)}})
            raise he

     
        except Exception as e:
            logger.error(
                f"Failed to generate enhance response and store text due to: {e}",
                extra={"tags": {"endpoint": "/enhance-response-generation", "thread_id": chat_input.query_id}})

