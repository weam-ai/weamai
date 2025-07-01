from fastapi import HTTPException
from src.logger.default_logger import logger
from src.chatflow_langchain.service.perplexity.browser_chat.system_conversation import PerplexityChatService 
class BrowserController:
    def __init__(self):
        self.managers = {
            "PERPLEXITY": PerplexityChatService,
        }
     
        self.code = None  # Initialize the code attribute

    def initialization_service_code(self, code: str = None):
        """
        Initializes the Browser Chat with the specified API key and company model.

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
                f"Failed to initialize Browser Service: {e}",
                extra={"tags": {"method": "BrowserController.initialization_service_code"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize Browser Controller: {e}")
    def _select_manager(self, chat_input):
        """
        Selects the appropriate manager based on the code.
        """
        return self.managers.get(self.code)()


    async def service_hub_handler(self, chat_input,**kwargs):
        """
        Handles the Browser input and returns the response.

        Parameters
        ----------
        chat_input : Any
            The input data for the chat.
        kwargs : Any
            Additional parameters.

        Returns
        -------
        response_generator : Any
            The response generator from the Tool manager.
        """
        try:
            browser_manager = self._select_manager(chat_input)
            if browser_manager is None:
                raise ValueError("Invalid Tool code provided.")
            
            browser_manager.initialize_llm(
            api_key_id=chat_input.llm_apikey,
            companymodel=chat_input.companymodel,
            thread_id=chat_input.thread_id,
            thread_model=chat_input.threadmodel,
            company_id=chat_input.company_id
        )
            browser_manager.initialize_repository(
                chat_session_id=chat_input.chat_session_id,
                collection_name=chat_input.threadmodel,
                regenerated_flag = chat_input.isregenerated,
                thread_id=chat_input.thread_id
            )
            # prompt attach
            browser_manager.prompt_attach(additional_prompt_id=chat_input.prompt_id,collection_name=chat_input.promptmodel)  
            
            ## conversation create
            browser_manager.create_conversation(input_text=chat_input.query,regenerate_flag = chat_input.isregenerated)  


            # streaming the chat chat serivce
            response_generator = browser_manager.stream_run_conversation(thread_id=chat_input.thread_id, \
                                                                            collection_name=chat_input.threadmodel,delay_chunk=chat_input.delay_chunk,regenerated_flag=chat_input.isregenerated,
                                                                            msgCredit=chat_input.msgCredit,is_paid_user=chat_input.is_paid_user)

                
            logger.info(
                "Successfully executed Browser chat API",
                extra={"tags": {"endpoint": "/stream-browser-chat"}}
            )
            return response_generator
        except HTTPException as e:
            raise e

        except Exception as e:
            logger.error(
                f"Failed to handle Browser Chat: {e}",
                extra={"tags": {"method": "BrowserController.service_hub_handler"}}
            )
            raise HTTPException(status_code=400, detail=e)
