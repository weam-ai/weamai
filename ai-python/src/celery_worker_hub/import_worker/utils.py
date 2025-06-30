from datetime import datetime
import pytz
from langchain.chains.llm import LLMChain
from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.messages import get_buffer_string
from celery.result import AsyncResult
from bson import ObjectId
from src.db.config import db_instance
from src.logger.default_logger import logger

# Initialize collections
chat_collection = db_instance.get_collection("chat")
chat_member_collection = db_instance.get_collection("chatMember")
messages_collection = db_instance.get_collection("messages")
importchat_collection = db_instance.get_collection("importChat")

def convert_to_ist(epoch_time):
    """
    Converts an epoch timestamp to IST (Indian Standard Time).
    """
    try:
        if epoch_time is None:
            raise ValueError("Provided epoch time is None.")
        
        # If epoch_time is a string, ensure it's converted to an integer
        if isinstance(epoch_time, str):
            epoch_time = float(epoch_time)  # Convert string to integer
        
        # Convert the epoch time to UTC first
        utc_time = datetime.fromtimestamp(epoch_time, tz=pytz.utc)
        
        # Convert the UTC time to IST (Indian Standard Time)
        ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
        # print("IST Time:", ist_time.isoformat())
        
        return ist_time
    
    except (ValueError, TypeError) as e:
        print(f"Error converting epoch time: {e}")
        return None
    
class SummarizerMixin:
    """Mixin for summarizer."""

    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    llm: BaseLanguageModel
    prompt: BasePromptTemplate
    summary_message_cls: BaseMessage = SystemMessage

    def predict_new_summary(self, messages, existing_summary):
        """Generate a new summary from the provided messages."""
        new_lines = get_buffer_string(
            messages,
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        return chain.predict(summary=existing_summary, new_lines=new_lines)


class ConversationSummaryMemory(BaseChatMemory, SummarizerMixin):
    """Conversation summarizer to chat memory."""

    buffer: str = ""

    def save_context(self, inputs, outputs):
        """Save context from this conversation to buffer."""
        super().save_context(inputs, outputs)
       

    def load_memory_variables(self, inputs: dict) -> dict:
        """Load memory variables from the current state of the memory."""
        return {"summary": self.buffer}
    
    def trigger_summary(self):
         self.buffer = self.predict_new_summary(
            self.chat_memory.messages[-2:], self.buffer
        )

    @property
    def memory_variables(self):
        """Return the list of memory variables."""
        return ["summary"]
    
def get_task_statuses(task_ids: list[str]) -> dict:
    """
    Asynchronously fetches the statuses of multiple Celery tasks and retrieves 
    the status of a specific key in their results.
    
    Args:
        task_ids (list[str]): A list of Celery task IDs.
        dict_key (str): The key to check in the task result dictionaries.

    Returns:
        dict: A dictionary of task statuses with their respective data or messages.
    """
    results = {}
    for task_id in task_ids:
        task_result = AsyncResult(task_id)
        status = task_result.status

        if status == 'SUCCESS':
            results[task_id] = "SUCCESS"
        elif status == 'PENDING':
            results[task_id] = "PENDING"
        elif status == 'FAILURE':
            results[task_id] = "FAILURE"
        else:
            results[task_id] = status
    
    return results

def convert_to_object_ids(ids):
    """Converts a list of string IDs to ObjectId instances if not already an ObjectId."""
    object_ids = []
    for chat_id in ids:
        if isinstance(chat_id, ObjectId):  # Check if it's already an ObjectId
            object_ids.append(chat_id)
        else:
            object_ids.append(ObjectId(chat_id))
    return object_ids

def delete_chat_members(chat_ids_list):
    """Deletes failed chat member records."""
    if chat_ids_list:
        object_ids = convert_to_object_ids(chat_ids_list)
        chat_member_collection.delete_many({"chatId": {"$in": object_ids}})
        logger.info(f"Deleted chat members for chat IDs: {chat_ids_list}")

def delete_messages(chat_ids_list):
    """Deletes failed messages linked to the failed chat IDs and import ID."""
    if chat_ids_list:
        object_ids = convert_to_object_ids(chat_ids_list)
        messages_collection.delete_many({"chatId": {"$in": object_ids}})
        logger.info(f"Deleted messages for chat IDs: {chat_ids_list}")

def delete_chats(chat_ids_list):
    """Deletes failed chat records."""
    if chat_ids_list:
        object_ids = convert_to_object_ids(chat_ids_list)
        chat_collection.delete_many({"_id": {"$in": object_ids}})
        logger.info(f"Deleted chats for chat IDs: {chat_ids_list}")

def delete_import_chat(import_id, chat_ids_list):
    if not chat_ids_list:
        logger.warning("No chat IDs provided for removal.")
        return "No chat IDs provided for removal."

    # Build the $unset query dynamically
    unset_query = {f"conversationData.{chat_id}": "" for chat_id in chat_ids_list}

    # Perform the update to remove the specified chat objects
    result = importchat_collection.update_one(
        {"_id": ObjectId(import_id)},
        {"$unset": unset_query}
    )

    if result.modified_count > 0:
        logger.info(f"Successfully removed {result.modified_count} chat objects from import ID: {import_id}")
        return f"Successfully removed {result.modified_count} chat objects."
    else:
        logger.warning(f"No chat objects were removed (check import_id: {import_id} or chat IDs).")
        return "No chat objects were removed (check import_id or chat IDs)."

def delete_failed_records(import_id,chat_ids_list):
    """Calls the specific delete functions for each collection."""
    if chat_ids_list:
        delete_chat_members(chat_ids_list)
        delete_messages(chat_ids_list)
        delete_chats(chat_ids_list)
        delete_import_chat(import_id,chat_ids_list)
        logger.info(f"Completed deletion of failed records for import ID: {import_id}")