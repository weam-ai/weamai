from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,GENAI_ERROR_MESSAGES_CONFIG,ANTHROPIC_ERROR_MESSAGES_CONFIG, WEAM_ROUTER_MESSAGES_CONFIG

class EnhanceRepostiory():
    """Repository for managing threads in a database."""
    def __init__(self):
        """
        Initialize the repository.

        Args:
            db_instance: An instance of the database.
        """
        self.db_instance = db_instance

    def initialization(self, query_id: str,chat_id:str,brain_id:str, collection_name: str):
        """
        Initialize the repository with thread ID and collection name.

        Args:
            thread_id (str): The ID of the thread.
            collection_name (str): The name of the collection.
        """
  
        self.query_id = query_id
        self.chat_id=ObjectId(chat_id),
        self.brain_id=ObjectId(brain_id)
        self.instance = self.db_instance.get_collection(collection_name)
        self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}


    async def fetch_max_version(self):
        """
        Fetch the document with the highest version number for the given query ID.

        Returns:
            dict: The document with the highest version number.

        Raises:
            ValueError: If no data is found for the given query ID.
        """

        query = {"queryId": ObjectId(self.query_id)}
        sort = {"versionNumber":-1}
        try:
            projection = {"versionNumber": 1}
            result = self.instance.find_one(query, projection=projection, sort=sort)
            self.current_max_version = result["versionNumber"] if result else 0
            logger.info(
                "Successfully accessed the database",
                extra={"tags": {
                    "method": "EnhancementRepostiory._fetch_max_version",
                    "query_id": self.query_id
                }}
            )
            return self.current_max_version
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "EnhancementRepostiory._fetch_max_version",
                    "query_id": self.query_id
                }}
            )
            return 0

    async def insert_new_record(self, data):
        """
        Insert a new record into the collection.

        Args:
            data (dict): Data to insert.
        """
        try:
            result =  self.instance.insert_one(data)
            logger.info(
                "Successfully inserted a new record",
                extra={"tags": {
                    "method": "EnhancementRepostiory.insert_new_record",
                    "query_id": self.query_id,
                    "inserted_id": str(result.inserted_id)
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while inserting a new record: {e}",
                extra={"tags": {
                    "method": "EnhancementRepostiory.insert_new_record",
                    "query_id": self.query_id
                }}
            )
    async def set_enhance_id(self):
        """
        Sets a new identifier for the instance.

        Args:
            id (str): The new identifier to be set.
        """
        self.enhance_id=str(ObjectId())
        return self.enhance_id

    def update_fields(self, data):
   
        """
        Update fields of the document.

        Args:
            data (dict): Data to update.
        """
        query = {'_id': ObjectId(self.enhance_id)}
        try:
            self.instance.update_one(query, data, upsert=True)
            logger.info(
                "Successfully updated the document fields",
                extra={"tags": {
                    "method": "EnhancementRepostiory.update_fields",
                    "document_id":self.enhance_id
                }}
            )
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the document fields: {e}",
                extra={"tags": {
                    "method": "EnhancementRepostiory.update_fields",
                    "document_id": self.enhance_id
                }}
            )
   
    def add_message_openai(self, error_code: str = "common_response") -> None:
        """
        Add an OpenAI-related message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))

        openai_message = {\
            
            "$set": {
                "chatId":self.chat_id,
                "brainId":self.brain_id,
                "openai_error": message
            }
        }
        self.update_fields(openai_message)


    def add_message_gemini(self, error_code: str = "common_response") -> None:
        """
        Add an hugging face message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = GENAI_ERROR_MESSAGES_CONFIG.get(error_code, GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))

        openai_message = {
            "$set": {
                "openai_error": message
            }
        }
        self.update_fields(openai_message)

    def add_message_anthropic(self, error_code: str = "common_response") -> None:
        """
        Add an hugging face message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))

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
    
    
    
    
