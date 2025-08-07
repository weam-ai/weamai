from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from langchain_core.messages import SystemMessage

class BrainRepository:
    """Repository for fetching brain data from the database."""

    def __init__(self):
        """
        Initialize the db_instance.
        """
        self.db_instance = db_instance
        self.brain_id = None
        self.brain_collection = None

    def initialization(self, brain_id: str = None):
        """
        Initialize the repository with brain ID.

        Args:
            brain_id (str): The ID of the brain.
        """
        self.brain_id = brain_id
        self.brain_collection = self.db_instance.get_collection('brain')

    def get_custom_instructions(self) -> SystemMessage:
        """
        Get the custom instructions from the brain data.

        Returns:
            SystemMessage: A SystemMessage containing the custom instructions, or None if not found.
        """
        try:

            if not self.brain_id:
                logger.info(
                    "No brain_id provided, skipping custom instructions fetch",
                    extra={"tags": {"method": "BrainRepository.get_custom_instructions"}}
                )
                return None

            brain = self.brain_collection.find_one({'_id': ObjectId(self.brain_id)})
            if brain and brain.get('customInstructions'):
                custom_instructions = brain.get('customInstructions')
                logger.info(
                    "Successfully fetched custom instructions",
                    extra={"tags": {"method": "BrainRepository.get_custom_instructions"}}
                )
                return SystemMessage(content=custom_instructions)
            else:
                logger.info(
                    "No custom instructions found for brain_id",
                    extra={"tags": {"method": "BrainRepository.get_custom_instructions"}}
                )
                return None
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "BrainRepository.get_custom_instructions",
                    "brain_id": self.brain_id
                }}
            )
            return None
        except Exception as e:
            logger.error(
                f"Failed to fetch custom instructions: {e}",
                extra={"tags": {"method": "BrainRepository.get_custom_instructions"}}
            )
            return None
