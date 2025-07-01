from fastapi import HTTPException, status
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.logger.default_logger import logger
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from src.celery_worker_hub.web_scraper.tasks.scrap_url import scrape_list_of_websites
from src.celery_worker_hub.web_scraper.tasks.summary import generate_list_summaries
from src.celery_worker_hub.web_scraper.tasks.db_dump import dump_to_db
from src.celery_worker_hub.web_scraper.tasks.notify import on_task_success,on_task_failed
from celery import chain 
from src.chatflow_langchain.service.weam_router.llama.scraper.config import ScraperConfig, GetLLMkey, DEFAULTMODEL
import gc
from src.chatflow_langchain.service.weam_router.llama.image.utils import extract_error_message
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG, WEAM_ROUTER_MESSAGES_CONFIG
from bson.objectid import ObjectId

# Initialize your repositories and services
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
prompt_repo = PromptRepository()

class OpenAIScrapUrlService():

    def initialize_llm(self, company_id: str = None, companymodel: str = None,llm_api_key_id:str=None):
        try:
            get_key = GetLLMkey()
            self.query = {
            "name": DEFAULTMODEL.GPT_4o_MINI,
            "company.id": ObjectId(company_id)
            }
            self.projection = {
                '_id': 1
            }
            llm_api_key_id = get_key.default_llm_key(company_id=company_id,query=self.query,projection= self.projection,companymodel=companymodel)
            llm_apikey_decrypt_service.initialization(llm_api_key_id, companymodel)
            self.llm = ChatOpenAI(
                model_name=llm_apikey_decrypt_service.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature', 0.7),
                api_key=llm_apikey_decrypt_service.decrypt()
            )
            logger.info("LLM successfully initialized.", extra={"tags": {"method": "ScrapUrlService.initialize_llm"}})
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}", extra={"tags": {"method": "ScrapUrlService.initialize_llm"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
    
    def initialize_prompt(self, prompt_ids: list = None, collection_name: str = None):
        self.collection_name= collection_name
        try:
            self.prompt_id=prompt_ids[0]
            prompt_repo.initialization(self.prompt_id, collection_name)
            
            logger.info("Prompt successfully initialized.", extra={"tags": {"method": "ScrapUrlService.initialize_prompt"}})
        except Exception as e:
            logger.error(f"Failed to initialize Prompt: {e}", extra={"tags": {"method": "ScrapUrlService.initialize_prompt"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize Prompt: {e}")
        
    def initialize_user_fcm(self, user_data):
        try:
            self.fcm_tokens = user_data.get('fcmTokens', [])
            user_id = user_data.get('_id')

            if self.fcm_tokens:
                logger.info(f"Retrieved FCM tokens for user {user_id}: {self.fcm_tokens}",
                            extra={"tags": {"method": "ScrapUrlService.initialize_user_fcm", "status_code": status.HTTP_200_OK}})
            else:
                logger.info(f"No FCM tokens found for user {user_id}",
                            extra={"tags": {"method": "ScrapUrlService.initialize_user_fcm", "status_code": status.HTTP_200_OK}})
        except HTTPException as e:
            logger.error(f"Failed to retrieve user data for FCM initialization: {e.detail}",
                         extra={"tags": {"method": "ScrapUrlService.initialize_user_fcm", "status_code": e.status_code}})
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during FCM initialization: {str(e)}",
                         extra={"tags": {"method": "ScrapUrlService.initialize_user_fcm", "status_code": status.HTTP_400_BAD_REQUEST}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize FCM Token: {e}")
    
    def scrape_website(self, parent_prompt_ids:str,child_prompt_ids:list=None,collection: str=None, user_data: dict= None):
        try:
            user_data = {
                "id": str(user_data["_id"]),
                "email": user_data["email"],
                "fname": user_data.get("fname", ""),
                "lname": user_data.get("lname", ""),
                "profile": {
                    "name": user_data.get("profile", {}).get("name", ""),
                    "uri": user_data.get("profile", {}).get("uri", ""),
                    "mime_type": user_data.get("profile", {}).get("mime_type", ""),
                    "id": str(user_data.get("profile", {}).get("id", ""))
                } if "profile" in user_data else None
            }
            available_info = prompt_repo.get_available_info()
            title = prompt_repo.get_prompt_title()
            brain_title = prompt_repo.get_brain_title()
            if available_info is not None:
                brain_slug = prompt_repo.get_brain_slug()
                brain_id = prompt_repo.get_brain_id()
                process_chain = chain(
                    scrape_list_of_websites.s(available_info,notification_data={"token": self.fcm_tokens,"user_data":user_data}),
                    generate_list_summaries.s(api_key=llm_apikey_decrypt_service.apikey,notification_data={"token": self.fcm_tokens,"user_data":user_data, "brain_id":brain_id}),
                    dump_to_db.s(parent_prompt_id=parent_prompt_ids[0],child_prompt_ids=child_prompt_ids,collection=collection)
                ).apply_async(
                    link=on_task_success.s(data={"token": self.fcm_tokens, "title": ScraperConfig.SUCCESS_TITLE.format(title=title,brain_title=brain_title), "body": ScraperConfig.SUCCESS_BODY.format(title=title,brain_title=brain_title),"user_data":user_data, "brain_id":brain_id}),
                    link_error=on_task_failed.s(data={"token": self.fcm_tokens, "title": ScraperConfig.FAILURE_TITLE.format(title=title,brain_title=brain_title), "body": ScraperConfig.FAILURE_BODY.format(title=title,brain_title=brain_title), "user_data":user_data, "brain_id":brain_id})
                )
                task_chain_id = process_chain.id
                logger.info(f"Scraping process started with chain ID: {task_chain_id}", extra={"tags": {"method": "ScrapUrlService.scrape_website"}})
                return task_chain_id
            else:
                prompt_repo.update_completed_flag()
                logger.info(f"No Website To scrape for id: {prompt_repo.prompt_id}", extra={"tags": {"method": "ScrapUrlService.scrape_website"}})
                return 'No Websites to scrape'
        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "ScrapUrlService.scrape_website.Exception_Try"}})
                else:
                    logger.error(
                        f"🚨 Failed to start the scraping process: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "ScrapUrlService.scrape_website.Exception_Try"}})
                prompt_repo.initialization(self.prompt_id, self.collection_name)
                prompt_repo.add_message_weam_router(error_code)
                content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
                raise HTTPException(status.HTTP_417_EXPECTATION_FAILED ,{"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content})

            except Exception as e:
                prompt_repo.initialization(self.prompt_id, self.collection_name)
                prompt_repo.add_message_weam_router("common_response")
                content = WEAM_ROUTER_MESSAGES_CONFIG.get("common_response")
                logger.error(f"🚨 Failed to start the scraping process: {e}", extra={"tags": {"method": "ScrapUrlService.scrape_website.Exception_Except"}})
                raise HTTPException(status.HTTP_400_BAD_REQUEST ,{"status": status.HTTP_400_BAD_REQUEST,"message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content})
        
        finally:
            self.cleanup()
    def cleanup(self):
        """
        Cleans up any resources or state associated with the service.
        """
        cleaned_up = []
        try:
            # List of attributes to clean up
            attributes = [
                'llm',
                'fcm_tokens',
                'query',
                'projection',
                'prompt_id'
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
                    extra={"tags": {"method": "ScrapUrlService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "ScrapUrlService.cleanup"}}
            )


