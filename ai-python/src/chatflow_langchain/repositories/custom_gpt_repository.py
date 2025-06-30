from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.abstract_custom_gpt_repository import AbstractCustomGPTRepository

class CustomGPTRepository(AbstractCustomGPTRepository):
    """Repository for managing Custom GPT in a database."""

    def __init__(self):
        """
        Initialize the db_instance.

        Args:
            db_instance: An instance of the database.
        """
        self.db_instance = db_instance

    def initialization(self, custom_gpt_id: str, collection_name: str):
        """
        Initialize the repository with Custom GPT ID and collection name.

        Args:
            custom_gpt_id (str): The ID of the Custom GPT.
            collection_name (str): The name of the collection.
        """
        self.custom_gpt_id = custom_gpt_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result = self._fetch_custom_gpt_model_data()
        

    def _fetch_custom_gpt_model_data(self):
        """Fetch data related to the custom gpt model."""
        query = {'_id': ObjectId(self.custom_gpt_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for prompt id: {self.custom_gpt_id}")
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "CustomGPTRepository._fetch_custom_gpt_model_data",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository._fetch_custom_gpt_model_data",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise

    
    def get_name(self):
        """Get the name  from the custom gpt model data."""
        try:
            return self.result['title']
        except KeyError as e:
            logger.error(
                f"Key error while getting content: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_content",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting content: {e}")
    def get_gpt_llm_key_id(self):
        """Get the gpt's llm models api key from the custom gpt model data."""
        try:
            llm_key_id = self.result.get('responseModel', {}).get('id', None)
            return llm_key_id
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_llm_key_id",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting llm_api_key id: {e}")
        
    def get_gpt_file_tag(self):
        """Get the gpt's file tag  from the custom gpt model data."""
        try:

            return self.result['doc']['uri'].split("/")[-1]
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_file_tag",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting gpt file id: {e}")

    def get_gpt_file_tag_list(self):
        """Get the gpt's file tag from the custom gpt model data."""
        try:
            if 'doc' not in self.result:
                return []
            if isinstance(self.result['doc'], list):
                tags = [doc['uri'].split("/")[-1] for doc in self.result['doc']]
            else:
                tags = [self.result['doc']['uri'].split("/")[-1]]
            return tags
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_file_tag",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting gpt file id: {e}")
        
    def get_gpt_file_ids(self):
        """Get the gpt's file tag from the custom gpt model data."""
        try:
            if 'doc' not in self.result:
                return []
            if isinstance(self.result['doc'], list):
                ids = [str(doc['id']) for doc in self.result['doc']]
            else:
                ids = [str(self.result['doc']['id'])]
            return ids
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_file_ids",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting gpt file id: {e}")
    
    def get_gpt_brain_id(self):
        """Get the gpt's brain id  from the custom gpt model data."""
        try:
            return str(self.result['brain']['id'])
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_brain_id",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting gpt brain  id: {e}")
    
    
    def get_gpt_embedding_key(self):
        """Get the gpt's file id  from the custom gpt model data."""
        try:
            return str(self.result.get('embedding_model').get('id')) if self.result.get('embedding_model',None) is not None else None
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_embedding_key",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting embedding_key_id: {e}")
    
    def get_gpt_system_prompt(self):
        """Get the gpt system prompt from the custom gpt model data."""
        try:
            return self.result['systemPrompt'].replace("{", "{{").replace("}", "}}")
        except KeyError as e:
            logger.error(
                f"Key error while getting gpt system prompt: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_system_prompt",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting system prompt: {e}")
    
    def get_gpt_goals(self):
        """Get the gpt's goals from the custom gpt model data."""
        try:
            goals = "\n".join(self.result['goals']).replace("{", "{{").replace("}", "}}")

            return goals
        except KeyError as e:
            logger.error(
                f"Key error while getting goals: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_goals",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting goals: {e}")
        
    def get_gpt_instructions(self):
        """Get the gpt's instructions from the custom gpt model data."""
        try:
            list_instrunctions=self.result.get("instructions")
            if isinstance(list_instrunctions,list):
                instructions = "\n".join(list_instrunctions)
                return instructions.replace("{", "{{").replace("}", "}}")
            else:
                return ""
        except KeyError as e:
            logger.error(
                f"Key error while getting instruction: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_instructions",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting goals: {e}")
    
    def get_doc_flag(self):
        """check the custom gpt is contain doc or not."""
        try:

            if self.result.get('doc',None):
                return True 
            else:
                return False
        except KeyError as e:
            logger.error(
                f"Key error while getting gpt doc flag: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_system_prompt",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting doc flag: {e}")
        
    def get_img_flag(self):
        """check the custom gpt is contain doc or not."""
        try:

            if self.result.get('imageEnable',False):
                return True 
            else:
                return False
        except KeyError as e:
            logger.error(
                f"Key error while getting gpt doc flag: {e}",
                extra={"tags": {
                    "method": "CustomGPTRepository.get_gpt_system_prompt",
                    "custom_gpt_id": self.custom_gpt_id
                }}
            )
            raise KeyError(f"Key error while getting doc flag: {e}")
        
    