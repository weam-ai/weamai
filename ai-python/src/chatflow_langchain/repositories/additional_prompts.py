from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.abstract_prompt_repository import AbstractPromptRepository
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG, WEAM_ROUTER_MESSAGES_CONFIG
from src.celery_worker_hub.web_scraper.utils.map_new_summaries import map_new_websites
class PromptRepository(AbstractPromptRepository):
    """Repository for managing prompts in a database."""

    def __init__(self):
        """
        Initialize the repository.

        Args:
            db_instance: An instance of the database.
        """
        self.db_instance = db_instance

    def initialization(self, prompt_id: str, collection_name: str):
        """
        Initialize the repository with prompt ID and collection name.

        Args:
            prompt_id (str): The ID of the prompt.
            collection_name (str): The name of the collection.
        """
        self.prompt_id = prompt_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result = self._fetch_prompt_model_data()

    def _fetch_prompt_model_data(self):
        """Fetch data related to the prompt model."""
        query = {'_id': ObjectId(self.prompt_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for prompt id: {self.prompt_id}")
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "PromptRepository._fetch_prompt_model_data",
                    "prompt_id": self.prompt_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "PromptRepository._fetch_prompt_model_data",
                    "prompt_id": self.prompt_id
                }}
            )
            raise

    def get_content(self):
        """Get the content from the prompt model data."""
        try:
            return self.result['content']
        except KeyError as e:
            logger.error(
                f"Key error while getting content: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_content",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting content: {e}")
    
    def get_brand_info(self):
        """Get the brand info from the prompt model data."""
        try:
            return self.result.get("brandInfo", None)
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting brand info: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brand_info",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting brandInfo: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting brand info: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brand_info",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting brandInfo: {e}")

    
    def get_company_info(self):
        """Get the company info from the prompt model data."""
        try:
            return self.result.get("companyInfo", None)
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting company info: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_company_info",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting companyInfo: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting company info: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_company_info",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting companyInfo: {e}")
        
    def get_product_info(self):
        """Get the product info from the prompt model data."""
        try:
            return self.result.get("productInfo", None)
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting product info: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_product_info",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting productInfo: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting product info: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_product_info",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting productInfo: {e}")
        
    def summaries_exist(self,root_key:str,key="summaries"):
        '''checking the summaries key exists or not'''
        if key in self.result[root_key]:
            return True
        else:
            return False
        
    def delete_key_summary(self,summary_key='summaries'):
        delete_filter = {
            "$and": [
                {"_id": ObjectId(self.prompt_id)},
                {f'{summary_key}': {"$exists": True}}
            ]
        } # Delete the matching documents result = collection.delete_many(delete_filter)
        unset_fields = {f'{summary_key}': ""}
        update_operation = {
            "$unset": unset_fields
        }
        self.instance.update_many(delete_filter, update_operation)
        logger.info(
                "Successfully deleted Old format of summaries",
                extra={"tags": {
                    "method": "PromptRepository.delete_key_summary",
                    "prompt_id": self.prompt_id
                }}
            )
        
    def delete_summary(self,summary_key='summaries',list_of_website:list=None):
        delete_filter = {
            "$and": [
                {"_id": ObjectId(self.prompt_id)},
                {f'{summary_key}': {"$exists": True}}
            ]
        } # Delete the matching documents result = collection.delete_many(delete_filter)
        unset_fields = {f'{summary_key}.{key}': "" for key in list_of_website}
        update_operation = {
            "$unset": unset_fields
        }
        self.instance.update_many(delete_filter, update_operation)
        self.update_completed_flag()
        logger.info(
                "Successfully Deleted unnecessary website keys",
                extra={"tags": {
                    "method": "PromptRepository.delete_summary",
                    "prompt_id": self.prompt_id,
                    "hash_deleted":list_of_website
                }}
            )
        
    def get_available_info(self):
        """Get the available info from the prompt model data and return it as a key-value pair."""
        possible_keys = ["website"]
        for key in possible_keys:
            if key in self.result:
                value = self.result.get('website',None)
                if value is not None:
                    try:
                        summary_dict = self.get_existing_summaries()
                        new_websites,mapped_websites = map_new_websites(summary_dict,value)
                        if summary_dict is not None:
                            delete_hash_site = []
                            for website in summary_dict:
                                if website not in mapped_websites:
                                    delete_hash_site.append(website)
                            if(len(delete_hash_site)>0):
                                self.delete_summary(list_of_website=delete_hash_site)
                        if len(new_websites)>0:
                            summary_key = 'summaries'
                            return {summary_key: new_websites}
                        else:
                            return None
                    except AttributeError as e:
                        logger.error(
                            f"Attribute error while getting {key}: {e}",
                            extra={"tags": {
                                "method": "PromptRepository.get_available_info",
                                "prompt_id": self.prompt_id
                            }}
                        )
                        raise AttributeError(f"Attribute error while getting {key}: {e}")
                    except KeyError as e:
                        logger.error(
                            f"Key error while getting {key}: {e}",
                            extra={"tags": {
                                "method": "PromptRepository.get_available_info",
                                "prompt_id": self.prompt_id
                            }}
                        )
                        raise KeyError(f"Key error while getting {key}: {e}")
                    
    def get_existing_summaries(self):
        """Get the available info from the prompt model data and return it as a key-value pair."""
        possible_keys = ["summaries"]

        for key in possible_keys:
            if key in self.result:
                value = self.result.get(key,None)
                if value is not None:
                    try:
                        summary_dict=value
                        if isinstance(summary_dict,dict):
                            return summary_dict
                        else:
                            self.delete_key_summary()
                            return None
                    except AttributeError as e:
                        logger.error(
                            f"Attribute error while getting {key}: {e}",
                            extra={"tags": {
                                "method": "PromptRepository.get_existing_summaries",
                                "prompt_id": self.prompt_id
                            }}
                        )
                        raise AttributeError(f"Attribute error while getting {key}: {e}")
                    except KeyError as e:
                        logger.error(
                            f"Key error while getting {key}: {e}",
                            extra={"tags": {
                                "method": "PromptRepository.get_existing_summaries",
                                "prompt_id": self.prompt_id
                            }}
                        )
                        raise KeyError(f"Key error while getting {key}: {e}")
        
        # If no valid key with a dictionary value is found
        logger.warning(
            "No valid dictionary info found in the result",
            extra={"tags": {
                "method": "PromptRepository.get_existing_summaries",
                "prompt_id": self.prompt_id
            }}
        )
        return None
    
    def get_resource_info(self):
        """Get the available info from the prompt model data and return it as a key-value pair."""
        possible_keys = ["brandInfo", "companyInfo", "productInfo"]
        
        for key in possible_keys:
            if key in self.result:
                value = self.result.get(key)
                if value is not None:
                    try:
                        logger.info(f"Successfully retrieved '{key}' with value '{value}'")
                        return key,value
                    except AttributeError as e:
                        logger.error(
                            f"Attribute error while getting {key}: {e}",
                            extra={"tags": {
                                "method": "PromptRepository.get_available_info",
                                "prompt_id": self.prompt_id
                            }}
                        )
                        raise AttributeError(f"Attribute error while getting {key}: {e}")
                    except KeyError as e:
                        logger.error(
                            f"Key error while getting {key}: {e}",
                            extra={"tags": {
                                "method": "PromptRepository.get_available_info",
                                "prompt_id": self.prompt_id
                            }}
                        )
                        raise KeyError(f"Key error while getting {key}: {e}")
        
        # If no valid key with a dictionary value is found
        logger.warning(
            "No valid dictionary info found in the result",
            extra={"tags": {
                "method": "PromptRepository.get_available_info",
                "prompt_id": self.prompt_id
            }}
        )
        return None,None
    
    def get_prompt_title(self):
        """Get the title from the prompt model data."""
        try:
            return self.result.get("title", None)
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting title: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_prompt_title",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting title: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting title: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_prompt_title",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting title: {e}")
        
    def get_brain_title(self):
        """Get the title from the brain data."""
        try:
            return self.result.get("brain", {}).get("title", None)
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting brain title: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brain_title",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting brain title: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting brain title: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brain_title",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting brain title: {e}")
        
    def get_brain_slug(self):
        """Get the slug from the brain data."""
        try:
            return self.result.get("brain", {}).get("slug", None)
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting brain slug: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brain_slug",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting brain slug: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting brain slug: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brain_slug",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting brain slug: {e}")
        
    def get_brain_id(self):
        """Get the slug from the brain data."""
        try:
            return self.result.get("brain", {}).get("id", None)
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting brain id: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brain_id",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting brain slug: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting brain id: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_brain_id",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting brain id: {e}")
        
    def get_websites(self):
        """Get the websites."""
        try:
            return self.result.get("website", [])
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting website: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_website",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting website: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting website: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_website",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting website: {e}")
        
    def get_summaries(self):
        """Get the summaries."""
        try:
            return self.result.get("summaries", {})
        except AttributeError as e:
            logger.error(
                f"Attribute error while getting summaries: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_summaries",
                    "prompt_id": self.prompt_id
                }}
            )
            raise AttributeError(f"Attribute error while getting summaries: {e}")
        except KeyError as e:
            logger.error(
                f"Key error while getting summaries: {e}",
                extra={"tags": {
                    "method": "PromptRepository.get_summaries",
                    "prompt_id": self.prompt_id
                }}
            )
            raise KeyError(f"Key error while getting summaries: {e}")

    def update_fields(self, data):
        """
        Update fields of the thread model.

        Args:
            data (dict): Data to update.
        """
        query = {'_id': ObjectId(self.prompt_id)}
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the collection fields: {e}",
                extra={"tags": {
                    "method": "PromptRepository.update_fields",
                    "prompt_id": self.prompt_id
                }}
            )
    
    def add_message_openai(self, error_code: str = "common_response") -> None:
        """
        Add an OpenAI-related message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))

        openai_message = {
            "$set": {
                "openai_error": message
            }
        }
        self.update_fields(openai_message)

    def add_message_weam_router(self, error_code: str = "common_response") -> None:
        """
        Add an Weamrouter-related message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))

        openai_message = {
            "$set": {
                "openai_error": message
            }
        }
        self.update_fields(openai_message)

    def update_completed_flag(self):
        query = {'_id': ObjectId(self.prompt_id)}
        data = { "$set": {
                'isCompleted':True
            }}
        try:
            self.instance.update_one(query, data)
            logger.info(
                f"Successfully updated the completed flag field",
                extra={"tags": {
                    "method": "PromptRepository.update_completed_flag",
                    "prompt_id": self.prompt_id
                }}
            )
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the completed flag field: {e}",
                extra={"tags": {
                    "method": "PromptRepository.update_completed_flag",
                    "prompt_id": self.prompt_id
                }}
            )
        
