from fastapi import HTTPException, status
from src.logger.default_logger import logger
from src.chatflow_langchain.service.pro_agent.qa_special.service import WebQASpecialService
from src.chatflow_langchain.service.pro_agent.qa_special.utils import URLCheckerService
from src.chatflow_langchain.service.pro_agent.web_proposal.service import WebProposalService
from src.chatflow_langchain.service.pro_agent.video_analysis.video_chat import VideoChatService
from src.chatflow_langchain.service.pro_agent.video_analysis.video_chat_uri import VideoChatUriService
class ProAgentController:
    def __init__(self):
        self.managers = {
            "QA_SPECIALISTS": WebQASpecialService,
            "WEB_PROPOSAL":WebProposalService,
            "VIDEO_CALL_ANALYZER":VideoChatUriService,
            "VIDEO_CALL_CACHE":VideoChatService,
        }
        self.pro_agent_code = None  # Initialize the code attribute
        # Mapping service codes to handler methods
        self.service_handlers = {
            "QA_SPECIALISTS": self.qa_specialist_service,
            "WEB_PROPOSAL":self.web_proposal_service,
            "VIDEO_CALL_ANALYZER":self.video_chat_service,
            "VIDEO_CALL_URI":self.video_chat_service
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
                extra={"tags": {"method": "ProAgentController.initialization_service_code"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize ProAgentController: {e}")

    async def service_hub_handler(self, chat_input, current_user, **kwargs):
        """
        Handles the service execution based on the initialized service type.
        """
        try:
            # Retrieve the appropriate service class
            agent_class = self.managers.get(self.pro_agent_code)
            if not agent_class:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or missing service code.")

            # Instantiate the service class
            agent_manager = agent_class()
        
            service_handler = self.service_handlers.get(self.pro_agent_code)
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
                extra={"tags": {"method": "ProAgentController.service_hub_handler"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to handle service: {e}")

    async def qa_specialist_service(self, agent_manager, chat_input):
        """
        Handles QA Specialist-specific logic.
        """
         # Dynamically call the appropriate handler method
        try:
            checker = URLCheckerService(chat_input.query)
            # reachable, not_reachable = await checker.check_urls_async()
            reachable = await checker.check_urls_async_status()
            first_url = next(iter(reachable.keys()), None)
            first_reason = next(iter(reachable.values()), None)
            if not reachable:
                logger.warning("🌐❌ No reachable URLs found in the provided input.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No reachable URLs found.")
            chat_input.query = first_url
    
            await agent_manager.initilize_chat_input(chat_input)
            if first_reason == 'crawler_blocker':
                await agent_manager.crawler_blocked()
            else:    
                await agent_manager.scrape_whole_url_content()
            await agent_manager.create_batches()
            await agent_manager.initialize_llm()
            await agent_manager.multiple_segementations()
            await agent_manager.initialize_repository()
            await agent_manager.create_chain()
            response = agent_manager.process_checklist_items()
            return response
        
        except HTTPException as http_exc:
            raise http_exc  # Re-raise known HTTP exceptions
        except Exception as e:
            logger.error(
                f"Failed to handle QA Specialist service: {e}",
                extra={"tags": {"method": "ProAgentController.qa_specialist_service"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to handle QA Specialist service: {e}")

    async def web_proposal_service(self,agent_manager,chat_input):
        """
        Handles Web Proposal-specific logic.
        """
        try:
            checker = URLCheckerService(chat_input.query)
            reachable, not_reachable = await checker.check_urls_async()

            if not reachable:
                logger.warning("🌐❌ No reachable URLs found in the provided input.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No reachable URLs found.")
            
            chat_input.query = reachable[0]
            await agent_manager.initilize_chat_input(chat_input)
            await agent_manager.initialize_llm()
            await agent_manager.scrape_url_content()
            await agent_manager.initialize_repository()
            await agent_manager.create_chain()
            response = agent_manager.run_chain()
            return response
        except HTTPException as http_exc:
            raise http_exc
    
    async def video_chat_service(self,agent_manager,chat_input):
        """
        Handles Web Proposal-specific logic.
        """
        try:
            await agent_manager.initialize_chat_input(chat_input)
            await agent_manager.initialize_llm()
            await agent_manager.initialize_repository()
            response = agent_manager.run_chain()
            return response
        except HTTPException as http_exc:
            raise http_exc