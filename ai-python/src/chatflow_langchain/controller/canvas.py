from fastapi import HTTPException
from src.logger.default_logger import logger
from src.chatflow_langchain.service.huggingface.canvas.canvas_manager import  HFCanvasService
from src.chatflow_langchain.service.openai.canvas.canvas_manager import OpenAICanvasService
from src.chatflow_langchain.service.anthropic.canvas.canvas_manager import AnthropicCanvasService
from src.chatflow_langchain.service.gemini.canvas.canvas_manager import GeminiCanvasService
from src.chatflow_langchain.service.o1.canvas.canvas_manager import O1OpenAICanvasService
from src.chatflow_langchain.service.multimodal_router.canvas.canvas_manager import RouterCanvasService
from src.chatflow_langchain.service.weam_router.deepseek.canvas.canvas_manager import DeepSeekOpenAICanvasService
from src.chatflow_langchain.service.weam_router.llama.canvas.canvas_manager import LlamaOpenAICanvasService
from src.chatflow_langchain.controller.config import OpenAIAdvancedModels
class CanvasController:
    def __init__(self):
        self.managers = {
            "OPEN_AI": OpenAICanvasService,
            "HUGGING_FACE": HFCanvasService,
            "ANTHROPIC":AnthropicCanvasService,
            "GEMINI":GeminiCanvasService,
            "DEEPSEEK":RouterCanvasService,
            "LLAMA4":RouterCanvasService,
            "QWEN":RouterCanvasService,
            "GROK":RouterCanvasService
        }

        self.openai_advance_managers={
           "OPEN_AI_O1":O1OpenAICanvasService
        }

        self.code = None  # Initialize the code attribute


    def initialization_service_code(self, code: str = None):
        """
        Initializes the Canvas with the specified API key and company model.

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
                f"Failed to initialize Canvas: {e}",
                extra={"tags": {"method": "CanvasController.initialization_service_code"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize canvas manager: {e}")
    def _select_manager(self, chat_input):
        """
        Selects the appropriate manager based on the code.
        """
        if self.code == "OPEN_AI" and chat_input.model_name in OpenAIAdvancedModels.MODELS:
            return self.openai_advance_managers.get(OpenAIAdvancedModels.code)()
        return self.managers.get(self.code)()

    async def service_hub_handler(self, canvas_input, **kwargs):
        """
        Handles the canvas chat input and returns the response.

        Parameters
        ----------
        chat_input : Any
            The input data for the chat.
        kwargs : Any
            Additional parameters.

        Returns
        -------
        response_generator : Any
            The response generator from the canvas manager.
        """
        try:
            canvas_manager =self._select_manager(canvas_input)
            if canvas_manager is None:
                raise ValueError("Invalid canvas code provided.")
            
            canvas_manager.initialize_thread_data(
            thread_id=canvas_input.old_thread_id,
            collection_name=canvas_input.threadmodel,
            regenerated_flag=canvas_input.isregenerated
            )
            canvas_manager.extract_selected_text(start_index=canvas_input.start_index,end_index=canvas_input.end_index,user_query=canvas_input.query)
            canvas_manager.fetch_data(
                company_id=canvas_input.company_id,
                custom_gpt_collection=canvas_input.custom_gpt_collection,
                api_key_id=canvas_input.llm_apikey,
                companymodel=canvas_input.companymodel,
                companypinecone_collection=canvas_input.companypinecone,
                chat_doc_collection=canvas_input.chat_docs_collection
            )
        

            canvas_manager.create_chain()
        
            response_generator= canvas_manager.run_chain(
                    query=canvas_input.query,
                    new_thread_id=canvas_input.new_thread_id,
                    chat_session_id=canvas_input.chat_session_id,
                    chat_collection_name=canvas_input.threadmodel,
                    collection_name=canvas_input.threadmodel,
                    delay_chunk=canvas_input.delay_chunk,
                    msgCredit=canvas_input.msgCredit,
                    is_paid_user=canvas_input.is_paid_user)
            
            logger.info(
                "Successfully executed Canvas API",
                extra={"tags": {"endpoint": "/canvas-chat-generate", "chat_session_id": canvas_input.chat_session_id}}
            )
            return response_generator
        except HTTPException as e:
            raise e

        except Exception as e:
            logger.error(
                f"Failed to handle Canvas chat: {e}",
                extra={"tags": {"method": "CanvasController.service_hub_handler"}}
            )
            raise HTTPException(status_code=500, detail=f"Failed to handle Canvas chat: {e}")
