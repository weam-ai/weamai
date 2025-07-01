from fastapi import HTTPException
from src.logger.default_logger import logger
from src.chatflow_langchain.service.huggingface.doc.rag_conversation import  HFStreamingDocumentedChatService
from src.chatflow_langchain.service.openai.doc.rag_conversation import OpenAIStreamingDocumentedChatService
from src.chatflow_langchain.service.anthropic.doc.rag_conversation import AnthropicStreamingDocumentedChatService
from src.chatflow_langchain.service.gemini.doc.rag_conversation import GeminiStreamingDocumentedChatService
from src.chatflow_langchain.controller.config import OpenAIAdvancedModels
from src.chatflow_langchain.service.o1.doc.rag_conversation import O1StreamingDocumentedChatService
from src.chatflow_langchain.service.multimodal_router.doc.rag_conversation import RouterDocumentedService
from src.chatflow_langchain.service.weam_router.deepseek.doc.rag_conversation import WeamDeepSeekDocumentedService
from src.chatflow_langchain.service.weam_router.llama.doc.rag_conversation import WeamLlamaDocumentedService
class RAGController:
    def __init__(self):
        self.managers = {
            "OPEN_AI": OpenAIStreamingDocumentedChatService,
            "HUGGING_FACE": HFStreamingDocumentedChatService,
            "ANTHROPIC":AnthropicStreamingDocumentedChatService,
            "GEMINI":GeminiStreamingDocumentedChatService
        }
        self.openai_advance_managers={
           "OPEN_AI_O1":O1StreamingDocumentedChatService
        }
        self.weam_router={
            "DEEPSEEK":RouterDocumentedService,
            "LLAMA4":RouterDocumentedService,
            "QWEN":RouterDocumentedService,
            "GROK":RouterDocumentedService
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
                extra={"tags": {"method": "RAGController.initialization_service_code"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize RAG Controller: {e}")
    
    def _select_manager(self, chat_input):
        """
        Selects the appropriate manager based on the code.
        """
        if self.code == "OPEN_AI" and chat_input.model_name in OpenAIAdvancedModels.MODELS:
            return self.openai_advance_managers.get(OpenAIAdvancedModels.code)()
        if chat_input.provider == "WEAM":
            return self.weam_router.get(self.code)()
        return self.managers.get(self.code)()


    async def service_hub_handler(self, chat_input, **kwargs):
        """
        Handles the RAG chat input and returns the response.

        Parameters
        ----------
        chat_input : Any
            The input data for the chat.
        kwargs : Any
            Additional parameters.

        Returns
        -------
        response_generator : Any
            The response generator from the RAG manager.
        """
        try:
            rag_manager = self._select_manager(chat_input)
            if rag_manager is None:
                raise ValueError("Invalid RAG code provided.")
            
            rag_manager.initialize_llm(
            api_key_id=chat_input.llm_apikey,
            companymodel=chat_input.companymodel,
            thread_id=chat_input.thread_id,
            thread_model = chat_input.threadmodel
        )
            rag_manager.initialize_repository(
                chat_session_id=chat_input.chat_session_id,
                collection_name=chat_input.threadmodel,
                regenerated_flag=chat_input.isregenerated,
                thread_id = chat_input.thread_id
            )
            rag_manager.load_vector_store(
                company_apikey_id=chat_input.company_id,
                tag=chat_input.tag,
                namespace=chat_input.brain_id,
                companypinecone_collection=chat_input.companypinecone,
                company_model_collection=chat_input.companymodel,
                embedder_api_key_id=chat_input.embedding_api_key,
                file_id=chat_input.file_id,
                file_collection=chat_input.file_collection,
                chat_doc_collection=chat_input.chat_docs_collection,
                query=chat_input.query,
            )
            rag_manager.prompt_attach(additional_prompt_id=chat_input.prompt_id,collection_name=chat_input.promptmodel)
            rag_manager.create_conversation(tag=chat_input.tag,input_text=chat_input.query, image_url=chat_input.image_url, regenerated_flag=chat_input.isregenerated)

            response_generator = rag_manager.stream_run_conversation(chat_input.thread_id, chat_input.threadmodel,isMedia=chat_input.isMedia,delay_chunk=chat_input.delay_chunk,regenerated_flag=chat_input.isregenerated,msgCredit=chat_input.msgCredit,is_paid_user=chat_input.is_paid_user)
                
            logger.info(
                "Successfully executed Chat With Document Model API",
                extra={"tags": {"endpoint": "/streaming-chat-with-doc", "chat_session_id": chat_input.chat_session_id}}
            )
            return response_generator

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(
                f"Failed to handle RAG chat: {e}",
                extra={"tags": {"method": "RAGController.service_hub_handler"}}
            )
            raise HTTPException(status_code=500, detail=f"Failed to handle RAG chat: {e}")
