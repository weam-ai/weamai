from fastapi import HTTPException
from src.logger.default_logger import logger
from src.chatflow_langchain.service.huggingface.custom_gpt.custom_factory import HFCustomGPTManager
from src.chatflow_langchain.service.openai.custom_gpt.custom_factory import OpenAICustomGPTManager
from src.chatflow_langchain.service.o1.custom_gpt.custom_factory import O1CustomGPTManager
from src.chatflow_langchain.service.anthropic.custom_gpt.custom_factory import AnthropicCustomGPTManager
from src.chatflow_langchain.service.gemini.custom_gpt.custom_factory import GeminiCustomGPTManager
from src.chatflow_langchain.service.multimodal_router.custom_gpt.custom_factory import RouterCustomGPTManager
from src.chatflow_langchain.service.weam_router.deepseek.custom_gpt.custom_factory import WeamDeepSeekCustomGPTManager
from src.chatflow_langchain.service.weam_router.llama.custom_gpt.custom_factory import WeamLlamaCustomGPTManager
from src.chatflow_langchain.controller.config import OpenAIAdvancedModels
class CustomGPTController:
    def __init__(self):
        self.managers = {
            "OPEN_AI": OpenAICustomGPTManager,
            "HUGGING_FACE": HFCustomGPTManager,
            "ANTHROPIC":AnthropicCustomGPTManager,
            "GEMINI":GeminiCustomGPTManager
        }
        self.openai_advance_managers={
           "OPEN_AI_O1":O1CustomGPTManager
        }
        self.weam_router={
            "DEEPSEEK":RouterCustomGPTManager,
            "LLAMA4":RouterCustomGPTManager,
            "QWEN":RouterCustomGPTManager,
            "GROK":RouterCustomGPTManager
        }
     
        self.code = None  # Initialize the code attribute

    def initialization_custom_gpt_code(self, code: str = None):
        """
        Initializes the Custom GPT with the specified API key and company model.

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
                f"Failed to initialize custom GPT: {e}",
                extra={"tags": {"method": "CustomGPTController.initialization_custom_gpt_code"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize custom GPT: {e}")
    def _select_manager(self, chat_input):
        """
        Selects the appropriate manager based on the code.
        """
        if self.code == "OPEN_AI" and chat_input.model_name in OpenAIAdvancedModels.MODELS:
            return self.openai_advance_managers.get(OpenAIAdvancedModels.code)()
        if chat_input.provider == "WEAM":
            return self.weam_router.get(self.code)()
        return self.managers.get(self.code)()


    async def custom_gpt_hub_handler(self, chat_input, **kwargs):
        """
        Handles the custom GPT chat input and returns the response.

        Parameters
        ----------
        chat_input : Any
            The input data for the chat.
        kwargs : Any
            Additional parameters.

        Returns
        -------
        response_generator : Any
            The response generator from the custom GPT manager.
        """
        try:
            custom_gpt_manager =self._select_manager(chat_input)
            if custom_gpt_manager is None:
                raise ValueError("Invalid custom GPT code provided.")
            
            custom_gpt_manager.Initilization_custom_gpt(
                custom_gpt_id=chat_input.custom_gpt_id,
                customgptmodel=chat_input.customgptmodel,
            )
            response_generator = await custom_gpt_manager.custom_gpt_chat_handler(chat_input)
            
            logger.info(
                "Successfully executed Chat With Document Model API",
                extra={"tags": {"endpoint": "/streaming-custom-gpt-chat-with-doc", "chat_session_id": chat_input.chat_session_id}}
            )
            return response_generator
        except HTTPException as e:
            raise e

        except Exception as e:
            logger.error(
                f"Failed to handle custom GPT chat: {e}",
                extra={"tags": {"method": "CustomGPTController.custom_gpt_hub_handler"}}
            )
            raise HTTPException(status_code=500, detail=f"Failed to handle custom GPT chat: {e}")
