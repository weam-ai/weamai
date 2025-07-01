import json
from src.chatflow_langchain.repositories.import_chat_repository import ImportChatRepository
from fastapi import HTTPException,status
from src.logger.default_logger import logger

import_chat_repository = ImportChatRepository() 
class ImportDataJson:
    def __init__(self, import_id, json_file_bytes,config,brain_id):
        self.import_id = import_id
        self.json_file_bytes = json_file_bytes
        self.config = config
        self.brain_id=brain_id


    def insert_records(self, fileName,current_user,file_uri,conversation_file):
        self.result = import_chat_repository.insert_import_records(self.config, fileName,self.import_id,user_data=current_user,file_uri=file_uri,conversation_file=conversation_file)


    async def user_data_get(self):
        self.team_data=import_chat_repository.get_team_data(self.brain_id)
        self.user_data=import_chat_repository.get_user_data(self.brain_id)
        self.isShare = any(item.get("isShare", False) for item in self.team_data)
        self.team_dict={}
        if self.team_data:
            self.team_ids=[str(team["id"]) for item in self.team_data for team in item.get("teams", [])]
            for id in self.team_ids:
                self.team_dict[id]=import_chat_repository.get_team_users(id)

       
        
    async def extract_and_process_zip(self):
        """Extracts files from the ZIP and processes them based on content."""
        try:
            
            self.json_data = json.loads(self.json_file_bytes.decode("utf-8"))
        except json.JSONDecodeError:
                return {"error": "Invalid JSON file"}

           
                


        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(
                f"Failed to Extract and Process Zip: {e}",
                extra={"tags": {"method": "ImportData.extract_and_process_zip"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Failed to Extract and Process Zip: {e}")
