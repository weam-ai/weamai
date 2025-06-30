import zipfile
import json
from io import BytesIO
from src.chatflow_langchain.repositories.import_chat_repository import ImportChatRepository
from src.celery_worker_hub.import_worker.tasks.file_upload import zip_process_and_upload_files
from fastapi import HTTPException,status
from src.logger.default_logger import logger

import_chat_repository = ImportChatRepository() 
class ImportData:
    def __init__(self, import_id, zip_file_bytes,config,brain_id):
        self.import_id = import_id
        self.zip_file_bytes = zip_file_bytes
        self.config = config
        self.brain_id=brain_id


    def insert_records(self, fileName,current_user,file_uri,conversation_file):
        self.result = import_chat_repository.insert_import_records(self.config, fileName,self.import_id,user_data=current_user,file_uri=file_uri,conversation_file=conversation_file)


    async def user_data_get(self):
        self.team_data=import_chat_repository.get_team_data(self.brain_id)
        self.user_data=import_chat_repository.get_user_data(self.brain_id)
             
        self.team_dict={}
        if self.team_data:
            self.team_ids=[str(team["id"]) for item in self.team_data for team in item.get("teams", [])]
            for id in self.team_ids:
                self.team_dict[id]=import_chat_repository.get_team_users(id)

       
        
    async def extract_and_process_zip(self):
        """Extracts files from the ZIP and processes them based on content."""
        try:
            with zipfile.ZipFile(BytesIO(self.zip_file_bytes), 'r') as zip_ref:
                file_list = zip_ref.namelist()

                conversation_file = "conversations.json"
                html_files = [file for file in file_list if file.endswith('.html')]
                matching_file = next((file for file in file_list if file.endswith(conversation_file)), None)
                if matching_file:
                    print("\nConversation file found.")
                    zip_process_and_upload_files.apply_async(args=[self.zip_file_bytes,str(self.import_id)])
                    

                    with zip_ref.open(matching_file) as file:
                        json_data = json.load(file)
                        self.json_data = json_data
                        

                    # Call appropriate processing function based on HTML file presence
                    self.html_files = html_files
                else:
                    raise HTTPException(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        detail="There was an error importing your chats. Please try again.")

        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(
                f"Failed to Extract and Process Zip: {e}",
                extra={"tags": {"method": "ImportData.extract_and_process_zip"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Failed to Extract and Process Zip: {e}")
