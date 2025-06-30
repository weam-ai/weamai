from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.file_abstract_repository import FileAbstractRepository
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG

class FileRepository(FileAbstractRepository):
    """
    A repository class for handling file-related database operations.
    Inherits from the FileAbstractRepository and interacts with a database instance.
    """

    def __init__(self):
        """
        Initializes the FileRepository with a database instance.
        """
        self.db_instance = db_instance


    def initialization(self, file_id, collection_name):
        """
        Initializes the repository with the specified file and collection.

        Args:
            file_id (str): The unique identifier of the file.
            collection_name (str): The name of the collection within the database.

        Sets:
            self.file_id (str): Stores the provided file ID.
            self.instance: Stores the collection reference from the database.
            self.result (dict): Stores the fetched file model data from the database.
        """
        self.file_id = file_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result = self._fetch_file_model_data()

    def get_embedding_key(self):
        """
        Retrieves the embedding API key from the fetched file model data.

        Returns:
            str: The embedding API key as a string.
        """
        try:
            return str(self.result['embedding_api_key'])
        except KeyError as e:
            logger.error(
                f"Key error while getting tag: {e}",
                extra={"tags": {
                    "method": "FileRepository.get_embedding_key",
                    "api_id": self.file_id
                }}
            )
            return None


    def _fetch_file_model_data(self):
        query = {"_id": ObjectId(self.file_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for file id: {self.file_id}")
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "FileRepository._fetch_file_model_data",
                    "api_id": self.file_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "FileRepository._fetch_file_model_data",
                    "thread_id": self.file_id
                }}
            )

    def get_tag(self):
        try:
            return self.result['name']
        except KeyError as e:
            logger.error(
                f"Key error while getting tag: {e}",
                extra={"tags": {
                    "method": "FileRepository.get_tag",
                    "api_id": self.file_id
                }}
            )
            raise KeyError(f"Key error while getting tag: {e}")

    def update_tokens(self,token_data):
        query = {'_id': ObjectId(self.file_id)}
        try:
            self.instance.update_one(query, token_data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the token fields: {e}",
                extra={"tags": {
                    "method": "FileRepository.update_token_fields",
                    "file_id": self.file_id
                }}
            )

    def update_fields(self, data):
        """
        Update fields of the vector model.

        Args:
            data (dict): Data to update.
        """
        query = {'_id': ObjectId(self.file_id)}
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the collection fields: {e}",
                extra={"tags": {
                    "method": "FileRepository.update_fields",
                    "thread_id": self.file_id
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

    def get_s3file_tag(self):
        """Get the s3 file tag id  from the file model data."""
        try:
            return self.result['uri'].split("/")[-1]
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_file_tag",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting gpt file id: {e}")
    
    def insert_file(self, collection_name:str, file_data:dict):
        """
        Insert a new file record into the database.

        Args:
            file_data (dict): The data of the file to be inserted.
        """
        try:
            self.instance = self.db_instance.get_collection(collection_name)
            result_id=self.instance.insert_one(file_data)
            logger.info(
                "File inserted successfully",
                extra={"tags": {
                    "method": "FileRepository.insert_file",
                }}
            )
            
            return str(result_id.inserted_id)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while inserting the file: {e}",
                extra={"tags": {
                    "method": "FileRepository.insert_file"
                }}
            )