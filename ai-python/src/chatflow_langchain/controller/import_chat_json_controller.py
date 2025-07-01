from src.chatflow_langchain.service.import_chat.import_json import ImportDataJson
from src.celery_worker_hub.import_worker.tasks.file_upload import upload_stream_to_s3
from src.chatflow_langchain.service.import_chat.openai_import import ImportOpenAIProcessor
from src.chatflow_langchain.service.import_chat.anthropic_import import ImportAnthropicProcessor
from fastapi import HTTPException
from src.logger.default_logger import logger
import os
from fastapi import status

class ImportChatController:
    def __init__(self):
        self.controller={"OPENAI":ImportOpenAIProcessor,"ANTHROPIC":ImportAnthropicProcessor}


    def initialize(self,import_id,import_input):
       self.import_id = import_id
       self.import_input = dict(import_input)

    async def upload_file(self,file,file_content):
        try:
            self.file = file
            self.file_content = file_content
            s3_bucket = os.environ.get("AWS_BUCKET", "gocustomai")
            # self.file_uri = f"importdata/{str(self.import_id)}/{self.file.filename}"
            self.file_uri = f" "

            self.conversation_file = f"importdata/{str(self.import_id)}/conversations.json"
            upload_stream_to_s3.apply_async(args=[self.file_content,s3_bucket,self.conversation_file])
        except Exception as e:
            logger.error(
                f"Failed to Upload file: {e}",
                extra={"tags": {"method": "ImportChatController.upload_file"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to Upload File: {e}")

    async def get_import_data(self,current_user):
        try:
            self.current_user = current_user
            self.import_data_service = ImportDataJson(import_id=self.import_id, json_file_bytes=self.file_content,config=self.import_input,brain_id=self.import_input['brain_id'])
            self.import_data_service.insert_records(self.file.filename,current_user,self.file_uri,self.conversation_file)
            await self.import_data_service.extract_and_process_zip()
            await self.import_data_service.user_data_get()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Failed to Retrieve Import Data: {e}",
                extra={"tags": {"method": "ImportChatController.get_import_data"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to Get Import Data: {e}")


    def pipeline_initlization(self,code:str):
 
        self.service=self.controller[code]()  

    
    async def process_conversations(self):
        try:
            await self.service.initlization(import_input=self.import_input,user_data=self.import_data_service.user_data,team_dict=self.import_data_service.team_dict,current_user=self.current_user,isShare=self.import_data_service.isShare)
            await self.service.conversations_transformations(json_data=self.import_data_service.json_data,import_id=self.import_id)
            logger.info("Conversation processing completed successfully.",
                extra={"tags": {"method": "ImportChatController.process_conversations"}})
        except Exception as e:
            logger.error(
                f"Failed to Process Conversations: {e}",
                extra={"tags": {"method": "ImportChatController.process_conversations"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to Process Conversations: {e}")