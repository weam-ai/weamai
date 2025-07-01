from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.setting_abstract_repository import SettingAbstractRepository
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG

class SettingRepository(SettingAbstractRepository):
    """
    A repository class for handling settings-related database operations.
    Inherits from the SettingAbstractRepository and interacts with a database instance.
    """

    def __init__(self):
        """
        Initializes the FileRepository with a database instance.
        """
        self.db_instance = db_instance


    def initialization(self,collection_name):
        """
        Initializes the repository with the specified file and collection.

        Args:
            collection_name (str): The name of the collection within the database.

        Sets:
            self.instance: Stores the collection reference from the database.
            self.result (dict): Stores the fetched file model data from the database.
        """
        self.instance = self.db_instance.get_collection(collection_name)

    def get_storage_configs(self):
        """
        Fetches the storage configurations from the database.

        Returns:
            dict: The storage configurations if found, otherwise an empty dictionary.
        """
        try:
            result = self.instance.find_one({"code": "STORAGE"})
            if result:
                return result
        except PyMongoError as e:
            logger.error(f"Error fetching storage configs: {e}")
            return {}