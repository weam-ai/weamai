from fastapi import HTTPException, status
from src.logger.default_logger import logger
from src.chatflow_langchain.service.pro_agent.sales_call_analyzer.audio_service import SalesAudioService
from src.chatflow_langchain.service.pro_agent.sales_call_analyzer.transcript_service import SalesTranscriptService
from src.chatflow_langchain.service.pro_agent.sales_call_analyzer.fathom_service import SalesFathomService


class SalesAnalyzerAgentController:
    def __init__(self):
        self.managers = {
            "AUDIO": SalesAudioService,
            "TRANSCRIPT":SalesTranscriptService,
            "FATHOM":SalesFathomService
        }
        self.pro_agent_code = None  # Initialize the code attribute
       
        # Mapping service codes to handler methods
        self.service_handlers = {
            ("SALES_CALL_ANALYZER","AUDIO"): self.zoom_audio_serivce,
            ("SALES_CALL_ANALYZER","TRANSCRIPT"):self.transcript_analyze_service,
            ("SALES_CALL_ANALYZER","FATHOM"):self.fathom_service
        }

    def initialization_service_code(self, pro_agent_code: str = None):
        """
        Initializes the service with the specified code.
        """
        try:
            self.pro_agent_code = pro_agent_code
        except Exception as e:
            logger.error(
                f"Failed to initialize ProAgent: {e}",
                extra={"tags": {"method": "SalesAnalyzerAgentController.initialization_service_code"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize SalesAnalyzerAgentController: {e}")

    async def service_hub_handler(self, chat_input, current_user, **kwargs):
        """
        Handles the service execution based on the initialized service type.
        """
        try:
            # Retrieve the appropriate service class
            agent_class = self.managers.get(chat_input.service_code)
            if not agent_class:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or missing service code.")

            # Instantiate the service class
            agent_manager = agent_class()
        
            service_handler = self.service_handlers.get((self.pro_agent_code,chat_input.service_code))
            if not service_handler:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported service type.")
         
            response =  await service_handler(agent_manager, chat_input)

            logger.info(
                f"Successfully executed service: {self.pro_agent_code}",
                extra={"tags": {"endpoint": "/service-hub"}}
            )
            return response

        except HTTPException as e:
            raise e

        except Exception as e:
            logger.error(
                f"Failed to handle service: {e}",
                extra={"tags": {"method": "SalesAnalyzerAgentController.service_hub_handler"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to handle service: {e}")

    async def zoom_audio_serivce(self, agent_manager, chat_input):
        """
        Handles Sales Call analyzer Audio with url service.
        """
         # Dynamically call the appropriate handler method
        try:
    
            await agent_manager.initilize_chat_input(chat_input)
            await agent_manager.initialize_llm()
            await agent_manager.initialize_repository()
            await agent_manager.upload_file()
            await agent_manager.create_chain()
            response = agent_manager.run_chain()
            return response
        
        except HTTPException as http_exc:
            raise http_exc  # Re-raise known HTTP exceptions
        except Exception as e:
            logger.error(
                f"Failed to handle Sales Call Analyzer service: {e}",
                extra={"tags": {"method": "SalesAnalyzerAgentController.zoom_audio_serivce"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to handle Sales Call Analyzer service: {e}")
        
    async def transcript_analyze_service(self, agent_manager, chat_input):
        """
        Handles Sales Call analyzer Audio with url service.
        """
         # Dynamically call the appropriate handler method
        try:
    
            await agent_manager.initilize_chat_input(chat_input)
            await agent_manager.initialize_llm()
            await agent_manager.initialize_repository()
            await agent_manager.create_chain()
            response = agent_manager.run_chain()
            return response
        
        except HTTPException as http_exc:
            raise http_exc  # Re-raise known HTTP exceptions
        except Exception as e:
            logger.error(
                f"Failed to handle Sales Call Analyzer service: {e}",
                extra={"tags": {"method": "SalesAnalyzerAgentController.transcript_analyze_service"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to handle Sales Call Analyzer service: {e}")
        
    async def fathom_service(self, agent_manager, chat_input):
        """
        Handles Sales Call analyzer Audio with url service.
        """
         # Dynamically call the appropriate handler method
        try:
    
            await agent_manager.initilize_chat_input(chat_input)
            await agent_manager.initialize_llm()
            await agent_manager.fetch_transcript_and_summary()
            await agent_manager.initialize_repository()
            await agent_manager.create_chain()
            response = agent_manager.run_chain()
            return response
        
        except HTTPException as http_exc:
            raise http_exc  # Re-raise known HTTP exceptions
        except Exception as e:
            logger.error(
                f"Failed to handle Sales Call Analyzer service: {e}",
                extra={"tags": {"method": "SalesAnalyzerAgentController.fathom_service"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to handle Sales Call Analyzer service: {e}")