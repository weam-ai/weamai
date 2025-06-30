from bson import ObjectId
from src.chatflow_langchain.service.import_chat.utils import create_chat_id
from src.celery_worker_hub.import_worker.tasks.extract_transform_openai import extract_and_transform_openai
from src.celery_worker_hub.import_worker.tasks.bulk_update import bulk_update_task,on_task_success
import hashlib
from datetime import datetime, timezone
from celery import group,chain
from src.db.config import db_instance
from celery import chord
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.service.config.model_config_openai import DefaultGPTTextModelRepository
from src.chatflow_langchain.repositories.import_chat_repository import ImportChatRepository
from src.chatflow_langchain.service.import_chat.config import ImportChatConfig
import os

import_chat_repository = ImportChatRepository()
openai_llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
BATCH_SIZE = int(os.environ.get('IMPORT_BATCH_SIZE',5))
class ImportOpenAIProcessor:

    async def initlization(self, import_input,user_data,team_dict,current_user,isShare):
        self.db_instance = db_instance
        self.collection = self.db_instance.get_collection("messages")
        self.importChat_collection = self.db_instance.get_collection("importChat")
        self.config = import_input
        self.user_data=user_data
        self.team_dict=team_dict
        self.current_user = current_user
        self.isShare = isShare

    async def conversations_transformations(self, json_data, import_id):
        """Parallel processing for handling conversations."""
        formated_user_data = {
            "id": str(self.current_user["_id"]),
            "email": self.current_user["email"],
            "fname": self.current_user.get("fname", ""),
            "lname": self.current_user.get("lname", ""),
            "fcmtokens": self.current_user.get("fcmTokens", []),
            "profile": {
            **({"name": self.current_user["profile"]["name"]} if "name" in self.current_user["profile"] else {}),
            **({"uri": self.current_user["profile"]["uri"]} if "uri" in self.current_user["profile"] else {}),
            **({"mime_type": self.current_user["profile"]["mime_type"]} if "mime_type" in self.current_user["profile"] else {}),
            **({"id": str(self.current_user["profile"]["id"])} if "id" in self.current_user["profile"] else {})
            } if "profile" in self.current_user else {}
        }

        existing_hash_ids = await self._get_existing_hash_ids()

        totalImportChat = 0
        total_import_tokens = 0
        responseAPI = "OPENAI"


        batch_size = len(json_data) if len(json_data) < BATCH_SIZE else BATCH_SIZE
      
        default_api_key = DefaultGPTTextModelRepository(company_id=self.config['company_id'],companymodel=self.config["companymodel"])
        openai_api_key = default_api_key.get_default_model_key()
        openai_llm_apikey_decrypt_service.initialization(openai_api_key, self.config["companymodel"])
        api_key = openai_llm_apikey_decrypt_service.decrypt()
        model_id = import_chat_repository.get_model_id(ImportChatConfig.code['openai_code'])
        group_list = []
        json_data = json_data[::-1]
        for i in range(0, len(json_data), batch_size):
            batch = json_data[i:i + batch_size]
            tasks = []
            task_ids_list=[]
            conversation_details = []
            bulk_updates = []
            existing_chat_ids = []

            for conversation in batch:
                totalImportChat += 1
                conversation_id, last_msg_id, conversationId_msgId_concat_hash = await self._process_conversation(conversation)
                if (conversationId_msgId_concat_hash != None) and (conversationId_msgId_concat_hash not in existing_hash_ids):
                    chat_id = create_chat_id(self.config, conversation["title"],self.user_data,self.team_dict,self.current_user,import_id,self.isShare)
                    if self.current_user.get("profile", {}).get("id") is not None:
                        self.current_user['profile']['id'] = str(self.current_user['profile']['id'])
                    user_data = {
                        'email':self.current_user['email'],
                        **({"fname": self.current_user["fname"]} if "fname" in self.current_user else {}),
                        **({"lname": self.current_user["lname"]} if "lname" in self.current_user else {}),
                        **({"profile": self.current_user["profile"]} if "profile" in self.current_user else {})
                    }
                    chat_id = str(chat_id)
                    task = extract_and_transform_openai.s(self.config, conversation, chat_id, str(import_id),user_data,api_key,model_id)
                    tasks.append(task)
                    
                    bulk_updates.append({
                                "$set": {
                                    f"conversationData.{chat_id}": {
                                        "hashIds": conversationId_msgId_concat_hash,
                                        "ConversationIds": conversation_id,
                                        "LastMsgIds": last_msg_id,
                                        "taskstatus": "pending"
                                    },
                                    "updatedAt": datetime.now(timezone.utc)
                                }                 
                    })
                else:
                    if conversationId_msgId_concat_hash:
                        existing_chat_ids.append(conversationId_msgId_concat_hash)

            if len(tasks)>0:
                callable_data = {
                    "username": self.current_user.get("fname", ""),
                    "email": self.current_user['email'],
                    "source": "OPENAI",
                    "brain_id": self.config["brain_id"],
                    "brain_name": self.config["brain_title"],
                    "import_id":str(import_id)
                }

                group_task = chain(
                group(tasks),
                bulk_update_task.s(config=self.config, import_id=str(import_id), bulk_updates=bulk_updates)
                )
                group_list.append(group_task)

        if len(tasks)>0:      
            chain_task = chord(
            group(group_list),
            on_task_success.si(data=callable_data,user_data=formated_user_data)
            ).apply_async()
                
                    

        existing_hash_count = len(existing_chat_ids)

        await self._final_update(import_id, totalImportChat, responseAPI,existing_hash_count)

    async def _get_existing_hash_ids(self):
        existing_hash_ids = set()
        data = self.importChat_collection.find({"company.name": self.config["company_name"], "brain.id": ObjectId(self.config["brain_id"])})
        for doc in data:
            brain_id = doc.get("brain", {}).get("id")
            if brain_id:
                conversation_data = doc.get("conversationData")
                if isinstance(conversation_data, dict):
                    for i in conversation_data:
                        hash_ids = conversation_data[i].get("hashIds")
                        if hash_ids:
                            existing_hash_ids.add(hash_ids)


        return existing_hash_ids

    async def _process_conversation(self, conversation):
        conversation_id = conversation.get("id")
        filtered_sorted_mappings = sorted(
            [
                value for value in conversation.get("mapping", {}).values()
                if value and isinstance(value, dict) and value.get("message")
                and isinstance(value["message"], dict)
                and value["message"].get("create_time") is not None
                and value["message"].get("content", {}).get("parts")
                and any(isinstance(part, str) and part.strip() for part in value["message"]["content"].get("parts", []))
            ],
            key=lambda x: x["message"]["create_time"]
        )

        if filtered_sorted_mappings:
            last_message = filtered_sorted_mappings[-1]["message"]
            last_msg_id = last_message.get("id")
        else:
            return None, None, None

        conversationId_msgId_concat = f"{conversation_id}_{last_msg_id}"
        conversationId_msgId_concat_hash = hashlib.sha256(str(conversationId_msgId_concat).encode('utf-8')).hexdigest()
        print(f"Generated Hash: {conversationId_msgId_concat_hash}")
        return conversation_id, last_msg_id, conversationId_msgId_concat_hash

    async def _final_update(self, import_id, totalImportChat, responseAPI,existing_hash_count):
        final_status = "success" 
        self.importChat_collection.update_one(
            {"_id": import_id},
            {
                "$set": {
                    "updatedAt": datetime.now(timezone.utc),
                    "totalImportChat": totalImportChat,
                    "responseAPI": responseAPI,
                    "existingHashCount": existing_hash_count,
                    "status": final_status,
                    "totalImportedTokens":0,
                    "totalImportedTokens": 0,
                    "totalImportedPrompt":0,
                    "totalImportedCompletion":0,
                    "totalSummaryTokens":0,
                    "totalSummaryPrompt":0,
                    "totalSummaryCompletion":0
                }
            }
        )