from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from langchain_core.messages import SystemMessage
from datetime import datetime
from src.crypto_hub.utils.crypto_utils import MessageDecryptor
import os
import json

key = os.getenv("SECURITY_KEY").encode("utf-8")
decryptor = MessageDecryptor(key)

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
            
    async def update_custom_instructions(self, new_instructions: str) -> bool:
        """
        Update the customInstructions for the current brain.
        Ensures the instructions are stored as a string, appending to existing instructions.
        
        Args:
            new_instructions (str): The new custom instructions to append.
            
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            if not self.brain_id:
                logger.info(
                    "No brain_id provided, skipping custom instructions update",
                    extra={"tags": {"method": "BrainRepository.update_custom_instructions"}}
                )
                return False
            
            # Get current instructions
            brain = self.brain_collection.find_one({'_id': ObjectId(self.brain_id)})
            current_instructions = ""
            
            if brain and brain.get('customInstructions'):
                current_instructions = brain.get('customInstructions')
                # If current instructions are in array format, convert to string
                if isinstance(current_instructions, list):
                    current_instructions = " ".join(current_instructions)
            
            # Append new instructions to current instructions

            updated_instructions = new_instructions
                
            # Update the customInstructions and lastInstructionsRevision
            result = self.brain_collection.update_one(
                {'_id': ObjectId(self.brain_id)},
                {'$set': {
                    'customInstructions': updated_instructions,
                    'lastInstructionsRevision': datetime.now()
                }}
            )
            if result.modified_count > 0:
                logger.info(
                    "Successfully updated custom instructions",
                    extra={"tags": {"method": "BrainRepository.update_custom_instructions"}}
                )
                return True
            else:
                logger.info(
                    "No changes made to custom instructions",
                    extra={"tags": {"method": "BrainRepository.update_custom_instructions"}}
                )
                return False
                
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the database: {e}",
                extra={"tags": {
                    "method": "BrainRepository.update_custom_instructions",
                    "brain_id": self.brain_id
                }}
            )
            return False
        except Exception as e:
            logger.error(
                f"Failed to update custom instructions: {e}",
                extra={"tags": {"method": "BrainRepository.update_custom_instructions"}}
            )
            return False
            
    async def count_messages_since_last_revision(self) -> int:
        """
        Count messages for this brain since the last revision.
        
        Returns:
            int: The count of messages.
        """
        try:

            if not self.brain_id:
                return 0
                
            # Get the brain to check the last revision timestamp
            brain = self.brain_collection.find_one({'_id': ObjectId(self.brain_id)})
            if not brain:
                return 0
                
            # Get the last revision timestamp or use a default date if not present
            last_revision = brain.get('lastInstructionsRevision', datetime.min)
            
            # Get the messages collection
            messages_collection = self.db_instance.get_collection('messages')
            
            # Count messages created after the last revision
            message_count = messages_collection.count_documents({
                'brain.id': ObjectId(self.brain_id),
                'createdAt': {'$gt': last_revision}
            })
            
            logger.info(
                f"Brain {self.brain_id} has {message_count} messages since last revision",
                extra={"tags": {"method": "BrainRepository.count_messages_since_last_revision"}}
            )
            
            return message_count
            
        except Exception as e:
            logger.error(
                f"Error counting messages: {e}",
                extra={"tags": {"method": "BrainRepository.count_messages_since_last_revision"}}
            )
            return 0
            
    async def should_revise_instructions(self) -> bool:
        """
        Check if we should revise the customInstructions for this brain.
        This happens when there are 10 or more messages since the last revision.
        
        Returns:
            bool: True if revision is needed, False otherwise.
        """
        message_count = await self.count_messages_since_last_revision()
        return message_count >= 10
        
    async def get_recent_messages(self, limit: int = 10) -> list:
        """
        Get recent messages for this brain.
        
        Args:
            limit (int): Maximum number of messages to retrieve.
            
        Returns:
            list: List of recent messages with decrypted content.
        """
        try:
            if not self.brain_id:
                return []
                
            # Get the messages collection
            messages_collection = self.db_instance.get_collection('messages')
            
            # Get recent messages
            recent_messages = list(messages_collection.find(
                {'brain.id': ObjectId(self.brain_id)},
                {'message': 1, 'ai': 1}
            ).sort('createdAt', -1).limit(limit))
            
            # Decrypt the messages
            decrypted_messages = []
            for msg in recent_messages:
                decrypted_msg = msg.copy()
                
                # Decrypt user message if it exists and is encrypted
                if 'message' in msg and msg['message']:
                    try:
                        decrypted_msg['message'] = decryptor.decrypt(msg['message'])
                    except Exception as decrypt_error:
                        logger.warning(
                            f"Could not decrypt message, using as is: {decrypt_error}",
                            extra={"tags": {"method": "BrainRepository.get_recent_messages"}}
                        )
                
                # Decrypt AI response if it exists and is encrypted
                if 'ai' in msg and msg['ai']:
                    try:
                        decrypted_msg['ai'] = decryptor.decrypt(msg['ai'])
                    except Exception as decrypt_error:
                        logger.warning(
                            f"Could not decrypt AI response, using as is: {decrypt_error}",
                            extra={"tags": {"method": "BrainRepository.get_recent_messages"}}
                        )
                
                decrypted_messages.append(decrypted_msg)
            
            return decrypted_messages
            
        except Exception as e:
            logger.error(
                f"Error getting recent messages: {e}",
                extra={"tags": {"method": "BrainRepository.get_recent_messages"}}
            )
            return []
