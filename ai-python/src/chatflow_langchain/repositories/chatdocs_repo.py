from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.abstract_chat_doc import AbstractChatDocsRepository


class ChatDocsRepository(AbstractChatDocsRepository):
    """Concrete class for managing chat documents in a database."""

    def __init__(self):
        """
        Initialize the repository with a database instance.
        """
        self.db_instance = db_instance
        self.instance = None
        self.file_id_list = None
        self.chat_id_list = None

    def initialization(self, file_id_list: list, chat_id_list: list = None, collection_name: str = "chatdocs"):
        """
        Initialize the repository with a list of file IDs, optional chat IDs, and a collection name.

        Args:
            file_id_list (list): The list of file IDs.
            chat_id_list (list, optional): The list of chat IDs. Defaults to None.
            collection_name (str): The name of the collection. Defaults to "chatdocs".
        """
        self.file_id_list = file_id_list
        self.chat_id_list = chat_id_list
        self.instance = self.db_instance.get_collection(collection_name)
        self.results= self._fetch_chat_docs_model_data()

    def _fetch_chat_docs_model_data(self):
        """
        Fetch data related to the chat documents using a list of file IDs.

        Returns:
            list: A list of documents found in the database.

        Raises:
            ValueError: If no file IDs are provided.
            PyMongoError: If an error occurs while accessing the database.
        """
        if not self.file_id_list:
            raise ValueError("File ID list is not set or is empty")

        query = {'fileId': {'$in': [ObjectId(file_id) for file_id in self.file_id_list]}}
        projection={'brainId': 1,"_id": 0}
        try:
            results = self.instance.find(query,projection)
            results = list(results)
            if not results:
                logger.warning("No data found for the given file IDs")
            else:
                logger.info(
                    "Successfully retrieved documents",
                    extra={"tags": {
                        "method": "ChatDocsRepository.fetch_chat_docs_by_file_ids",
                        "file_ids": self.file_id_list
                    }}
                )
            return results
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "ChatDocsRepository.fetch_chat_docs_by_file_ids",
                    "file_ids": self.file_id_list
                }}
            )
            raise

    def get_brain_id_list(self):
        """
        Retrieves a list of brain IDs from the results.

        This method iterates over the `results` attribute, extracts the 'brainId' from each item,
        converts it to a string, and returns a list of these string representations.

        Returns:
            list: A list of brain IDs as strings.
        """
        brain_list = [str(i['brainId']) for i in self.results]
        return brain_list