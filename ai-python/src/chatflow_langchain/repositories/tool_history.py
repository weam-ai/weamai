from src.logger.default_logger import logger
import json
from typing import List, Union, Sequence, Dict
from pymongo import errors
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, message_to_dict, messages_from_dict
from bson.objectid import ObjectId
import os
from src.chatflow_langchain.utils.hash_generator import generate_unique_number
from src.chatflow_langchain.utils.tool_pipeline_query import get_pipeline_v2,get_latest_checkpoint,regenerate_history_pipeline,retrieve_thread_checkpoint
from src.db.config import db_instance
from src.crypto_hub.utils.crypto_utils import crypto_service
from dotenv import load_dotenv
from src.chatflow_langchain.repositories.config import HistoryConfig

load_dotenv()

# Default database and collection names
DEFAULT_DBNAME = "customai"
DEFAULT_COLLECTION_NAME = "messages"
FLAG_MAPPING = {(False):'simple_pipeline',(True):'regenerate_pipeline'}


class CustomAIMongoDBChatMessageHistory(BaseChatMessageHistory):
    def initialize(self, chat_session_id: str, collection_name: str = DEFAULT_COLLECTION_NAME,regenerated_flag:bool=False,thread_id:str=None) -> None:
        """
        Initialize the database connection and collection.

        Args:
            chat_session_id (str): The chat session identifier.
            collection_name (str): The name of the collection.
        """

        self.chat_session_id = chat_session_id
        self.regenerated_flag= regenerated_flag
        self.thread_id = thread_id
        self.memory_buffer = ''
       
        try:
            self.db =db_instance
            self.collection = self.db[collection_name]
            self.history_manager = {'simple_pipeline': self._retrieve_messages_from_db,'regenerate_pipeline': self._retrieve_messages_for_regeneration}
        except errors.ConnectionFailure as error:
            logger.error(f"Connection to MongoDB failed: {error}")

    def _retrieve_messages_from_db(self) -> List[Dict]:
        latest_checkpoint = get_latest_checkpoint(self.chat_session_id, self.db)
        if latest_checkpoint is not None:
            pipeline = get_pipeline_v2(self.chat_session_id, latest_checkpoint=latest_checkpoint)
        
            try:
                
                cursor = self.collection.aggregate(pipeline)
                return list(cursor)
            except errors.OperationFailure as error:
                logger.error(f"Failed to retrieve messages: {error}")
                return []
        else:
            return []
        
    def _retrieve_messages_for_regeneration(self) -> List[Dict]:
        latest_checkpoint,createdAt = retrieve_thread_checkpoint(self.thread_id, self.db)
        if latest_checkpoint is not None:
            pipeline = regenerate_history_pipeline(self.chat_session_id, latest_checkpoint=latest_checkpoint,createdAt=createdAt)
        
            try:
                
                cursor = self.collection.aggregate(pipeline)
                return list(cursor)
            except errors.OperationFailure as error:
                logger.error(f"Failed to retrieve messages: {error}")
                return []
        else:
            return []
        

    def _extract_messages(self, result_list: List[Dict]) -> List[Dict]:
        messages = []
        try:
            for res in result_list:
                summary_checkpoint = res.pop("sumhistory_checkpoint", None)
                if summary_checkpoint is not None:
                    self.summary_checkpoint = summary_checkpoint
                
                res.pop("chat_session_id", None)
                res.pop("_id", None)
                res.pop("createdAt",None)
                
                if res['img_gen_prompt'] is not None:
                    res['img_gen_prompt']=self.convert_img_gen_to_human(image_gen_prmpt=res['img_gen_prompt'])
                else:
                    res.pop('img_gen_prompt')

                if res['media'] is not None:
                    res['media']=self.convert_media_to_human(media=res['media'])
                else:
                    res.pop("media")
                messages.extend(list(res.values()))
            return messages
        except Exception as error:
            logger.error(f"Failed to extract messages: {error}")
            return []

    def _parse_messages(self, messages: List[Dict]) -> List[BaseMessage]:
        try:
            messages = [json.loads(crypto_service.decrypt(msg)) for msg in messages]
            return messages_from_dict(messages)
        except (json.JSONDecodeError, KeyError) as error:
            logger.error(f"Failed to parse messages: {error}")
            return []

    def _filter_system_messages(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        filtered_messages = []
        system_message_found = False
        for message in messages:
            if isinstance(message, SystemMessage):
                if not system_message_found:
                    filtered_messages.append(message)
                    system_message_found = True
                    self.memory_buffer = message.content
            else:
                if any(key in message.additional_kwargs for key in HistoryConfig.ADDITIONAL_KEYS):
                    message.content += str(message.additional_kwargs)
                filtered_messages.append(message)
        
        MESSAGES_BOUNDER=os.environ.get('MESSAGES_BOUNDER')
        if MESSAGES_BOUNDER == None:
            filtered_messages=filtered_messages
        elif MESSAGES_BOUNDER.strip() == "":
            filtered_messages=filtered_messages
        else:
            MESSAGES_BOUNDER = int(MESSAGES_BOUNDER)
            filtered_messages=filtered_messages[:MESSAGES_BOUNDER]
        return filtered_messages

    @property
    def messages(self) -> List[BaseMessage]:
        result_list = self.history_manager[FLAG_MAPPING[(self.regenerated_flag)]]()
        if not result_list:
            return []

        raw_messages = self._extract_messages(result_list)
        parsed_messages = self._parse_messages(raw_messages)
        return self._filter_system_messages(parsed_messages)

    def add_message(self, message: Union[BaseMessage, str], thread_id: str, message_type: str) -> None:
        """
        Add a message to the database.

        Args:
            message (Union[BaseMessage, str]): The message to add.
            thread_id (str): The thread identifier.
            message_type (str): The type of message ('system' or 'ai').
        """
        if message_type not in ["system", "ai"]:
            logger.error("Invalid message type. Must be 'system' or 'ai'.")
            return

        if isinstance(message, str):
            message = SystemMessage(content=message) if message_type == "system" else AIMessage(content=message)
        msg_dict = message_to_dict(message)

        try:
            upsert_query = {"chat_session_id": ObjectId(self.chat_session_id), "_id": ObjectId(thread_id)}
            upsert_update = {
                "$set": {
                    message_type: crypto_service.encrypt(json.dumps(msg_dict))
                }
            }
            if message_type == "system":
                if msg_dict['data']['content']=='':
                    upsert_update["$set"]["sumhistory_checkpoint"] = generate_unique_number(self.chat_session_id)
                else:
                    upsert_update["$set"]["sumhistory_checkpoint"] = generate_unique_number(msg_dict['data']['content'])

            self.collection.update_one(upsert_query, upsert_update, upsert=False)
        except errors.WriteError as err:
            logger.error(f"Failed to add {message_type} message: {err}")

    def add_message_with_kwargs(self, message: Union[BaseMessage, str], thread_id: str, message_type: str,**kwargs) -> None:
        """
        Add a message to the database.

        Args:
            message (Union[BaseMessage, str]): The message to add.
            thread_id (str): The thread identifier.
            message_type (str): The type of message ('system' or 'ai').
        """
        if message_type not in ["system", "ai"]:
            logger.error("Invalid message type. Must be 'system' or 'ai'.")
            return

        if isinstance(message, str):
            message = SystemMessage(content=message) if message_type == "system" else AIMessage(content=message,additional_kwargs=kwargs)
        msg_dict = message_to_dict(message)

        try:
            upsert_query = {"chat_session_id": ObjectId(self.chat_session_id), "_id": ObjectId(thread_id)}
            upsert_update = {
                "$set": {
                    message_type: crypto_service.encrypt(json.dumps(msg_dict))
                }
            }
            if message_type == "system":
                if msg_dict['data']['content']=='':
                    upsert_update["$set"]["sumhistory_checkpoint"] = generate_unique_number(self.chat_session_id)
                else:
                    upsert_update["$set"]["sumhistory_checkpoint"] = generate_unique_number(msg_dict['data']['content'])

            self.collection.update_one(upsert_query, upsert_update, upsert=False)
        except errors.WriteError as err:
            logger.error(f"Failed to add {message_type} message: {err}")

    def add_message_system(self, message: Union[SystemMessage, str], thread_id: str) -> None:
        """
        Add a system message to the database.

        Args:
            message (Union[SystemMessage, str]): The system message to add.
            thread_id (str): The thread identifier.
        """
        self.add_message(message, thread_id, "system")

    def add_ai_message(self, message: Union[AIMessage, str], thread_id: str) -> None:
        """
        Add an AI message to the database.

        Args:
            message (Union[AIMessage, str]): The AI message to add.
            thread_id (str): The thread identifier.
        """
        self.add_message(message, thread_id, "ai")
    
    def add_ai_message_kwargs(self, message: Union[AIMessage, str], thread_id: str,**kwargs) -> None:
        """
        Add an AI message to the database.

        Args:
            message (Union[AIMessage, str]): The AI message to add.
            thread_id (str): The thread identifier.
        """
        self.add_message_with_kwargs(message, thread_id,"ai",**kwargs)

    def clear(self) -> None:
        """
        Clear all messages for the current chat session.
        """
        try:
            self.collection.delete_many({"chat_session_id": ObjectId(self.chat_session_id)})
        except errors.WriteError as err:
            logger.error(f"Failed to clear messages: {err}")

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        '''
        implemnts the add messages if required
        currently we don't need for implementation this method
        '''
        pass

    def convert_media_to_human(self, media, **kwargs):
        if media:
            if isinstance(media, list):
                if len(media) > 0:
                    file_msg = []
                    file_flag = False
                    for file in media:
                        if file.get('name',None):
                            file_flag = True
                        # Safely get keys with defaults
                            file_name = file.get('name', '')
                            file_uri  = file.get('uri', '')
                            # If file_uri is empty, handle splitting gracefully
                            file_tag  = file_uri.split('/')[-1] if file_uri else ''
                        if file_flag:
                            file_msg.append(f"User file details - file_name: {file_name}, file_tag: {file_tag}")
                    message = " | ".join(file_msg)
                    return crypto_service.encrypt(json.dumps(message_to_dict(HumanMessage(content=message))))
                else:
                    return crypto_service.encrypt(json.dumps(message_to_dict(HumanMessage(content=''))))
            else:
                # Safely get keys with defaults
                if file.get('name',None):
                    file_name = media.get('name', '')
                    file_uri  = media.get('uri', '')
                    file_tag  = file_uri.split('/')[-1] if file_uri else ''
                    
                    message = f"User file details - file_name: {file_name}, file_tag: {file_tag}"

                    return crypto_service.encrypt(json.dumps(message_to_dict(HumanMessage(content=message))))
                else:
                    return crypto_service.encrypt(json.dumps(message_to_dict(HumanMessage(content=''))))
        else:
            # If media is falsy, return empty content
            return crypto_service.encrypt(json.dumps(message_to_dict(HumanMessage(content=''))))
    
    def convert_img_gen_to_human(self, image_gen_prmpt,**kwargs):
        if image_gen_prmpt:
           
            message = f"Previous image request: {image_gen_prmpt}"
            return crypto_service.encrypt(json.dumps(message_to_dict(HumanMessage(content=message))))
        else:
            return crypto_service.encrypt(json.dumps(message_to_dict(HumanMessage(content=''))))


    
