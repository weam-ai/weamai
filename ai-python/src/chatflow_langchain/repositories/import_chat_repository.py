from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from datetime import datetime, timezone

class ImportChatRepository():
    def __init__(self):
        self.db_instance = db_instance
        self.brain_collection = self.db_instance.get_collection("brain")
        self.shareBrain_collection = self.db_instance.get_collection("sharebrain")
        self.team_users_table = self.db_instance.get_collection("teamUser")
        self.model_table = self.db_instance.get_collection('model')

    def get_team_data(self, brain_id):
        try:
            team_data = self.brain_collection.find({"_id":ObjectId(brain_id)},{"teams":1,"isShare":1,"_id":0})
            team_data = list(team_data)
            return team_data
        except PyMongoError as e:
            logger.error(f"Failed to retrieve Team Data: {e}")
            return []   
        
    def get_user_data(self, brain_id):
        try:
            user_data = self.shareBrain_collection.find({"brain.id":ObjectId(brain_id)},{"user":1,"teamId":1,"invitedBy":1,"_id":0})
            user_data = list(user_data)
            return user_data
        except PyMongoError as e:
            logger.error(f"Failed to retrieve User data: {e}")
            return []
        
    def get_team_users(self, team_id):
        try:
            team_users = self.team_users_table.find({"_id":ObjectId(team_id)},{"teamUsers":1,"_id":0})
            team_users = list(team_users)
            return team_users
        except PyMongoError as e:
            logger.error(f"Failed to retrieve Team Users: {e}")
            return []
        
    def get_model_id(self,code):
        try:
            model_id = self.model_table.find({"code": code },{"_id": 1 })
            model_id = list(model_id)
            return str(model_id[0]['_id'])
        except PyMongoError as e:
            logger.error(f"Failed to retrieve Model ID: {e}")
            return []
        
    def insert_import_records(self,config, fileName,import_id,user_data,file_uri,conversation_file):
        """Function to handle the import of conversation data to MongoDB."""
    # Initialize metadata
        try:
            importTime = datetime.now(timezone.utc)

            # Insert initial "pending" status into `importChat`
            importChatData = {
                "_id": import_id,
                "user": {
                    "email": user_data["email"],
                    **({"fname": user_data["fname"]} if "fname" in user_data else {}),
                    **({"lname": user_data["lname"]} if "lname" in user_data else {}),
                    **({"profile": user_data["profile"]} if "profile" in user_data else {}),
                    "id": ObjectId(config["user_id"]),

                },
                "company": {
                    "name": config["company_name"],
                    "id": ObjectId(config["company_id"])
                },
                "brain": {
                    "title": config["brain_title"],
                    "slug": config["brain_slug"],
                    "id": ObjectId(config["brain_id"])
                },
                "fileDetails": {
                    "fileName": fileName,
                    "fileId": ObjectId(),
                    "uri":file_uri,
                    "jsonUri":conversation_file
                },
                "createdAt": importTime,
                "updatedAt": importTime,
                "totalImportChat": 0,
                "successImportedChat": 0,
                "totalImportedTokens": 0,
                "responseAPI": None,
                "status": "pending"
            }

            importChat_collection = self.db_instance.get_collection("importChat")
        

            # Insert the entire importData as a single record
            importChat_collection.insert_one(importChatData)
        except PyMongoError as e:
            logger.error(
                f"An error occurred Inserting Import Records: {e}",
                extra={"tags": {
                    "method": "ImportChatRepository.insert_import_records"
                }}
            )

        
        return importChatData, import_id