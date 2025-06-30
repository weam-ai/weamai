from fastapi import HTTPException
from src.logger.default_logger import logger
from src.chatflow_langchain.service.openai.scraper.scrap_url import OpenAIScrapUrlService

class ScrapeController:
    def __init__(self):
        self.managers = {
            "OPEN_AI": OpenAIScrapUrlService,
            "HUGGING_FACE": OpenAIScrapUrlService,
            "ANTHROPIC":OpenAIScrapUrlService,
            "GEMINI":OpenAIScrapUrlService
        }
     
        self.code = None  # Initialize the code attribute

    def initialization_service_code(self, code: str = None):
        """
        Initializes the Scraper with the specified API key and company model.

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
                f"Failed to initialize Scraping: {e}",
                extra={"tags": {"method": "ScrapeController.initialization_service_code"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize Scrape Controller: {e}")

    async def service_hub_handler(self, chat_input,current_user,**kwargs):
        """
        Handles the Scraping input and returns the response.

        Parameters
        ----------
        chat_input : Any
            The input data for the chat.
        kwargs : Any
            Additional parameters.

        Returns
        -------
        response_generator : Any
            The response generator from the Scrape manager.
        """
        try:
            scrape_manager = self.managers.get(self.code)()
            if scrape_manager is None:
                raise ValueError("Invalid Scraping code provided.")
            
            scrape_manager.initialize_llm(
                company_id=chat_input.company_id,
                companymodel=chat_input.companymodel,
                llm_api_key_id=chat_input.llm_apikey
            )

            # Initialize the prompt if needed
            scrape_manager.initialize_prompt(
                prompt_ids=chat_input.parent_prompt_ids,
                collection_name=chat_input.promptmodel
            )

            # Initialize user FCM token
            scrape_manager.initialize_user_fcm(current_user)

            # Perform the scraping
            scrape_response = scrape_manager.scrape_website(collection=chat_input.promptmodel,parent_prompt_ids=chat_input.parent_prompt_ids,\
                                                            child_prompt_ids=chat_input.child_prompt_ids,user_data=current_user)

                
            logger.info(
                "Successfully executed scrape website API",
                extra={"tags": {"endpoint": "/scrape-url"}}
            )
            return scrape_response
        
        except HTTPException as e:
            raise e

        except Exception as e:
            logger.error(
                f"Failed to handle Scraping: {e}",
                extra={"tags": {"method": "ScrapeController.service_hub_handler"}}
            )
            raise HTTPException(status_code=500, detail=f"Failed to handle Website scraping: {e}")
