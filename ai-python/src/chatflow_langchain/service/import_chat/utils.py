import pytz
from datetime import datetime
from bson import ObjectId
from src.db.config import db_instance


def create_chat_id(config, chat_title, user_data, team_dict,current_user,import_id,isShare):
    """Create a new chat ID and insert it into MongoDB."""
    timezone = pytz.timezone("Asia/Kolkata")
    current_datetime = datetime.now(timezone)
    chat_id = ObjectId()
    team_list = list(team_dict.keys())
    chat = [{
            "_id": chat_id,
            "user": {
                "email": current_user["email"],
                **({"fname": current_user["fname"]} if "fname" in current_user else {}),
                **({"lname": current_user["lname"]} if "lname" in current_user else {}),
                **({"profile": current_user["profile"]} if "profile" in current_user else {}),
                "id": ObjectId(config["user_id"])
            },
            "brain": {
                        "title": config["brain_title"],
                        "slug": config["brain_slug"],
                        "id": ObjectId(config["brain_id"])
                    },
            "importId":import_id,
            "isNewChat": True,
            "isShare": isShare,
            "teams": team_list,
            "createdAt": current_datetime,
            "updatedAt": current_datetime,
            "__v": 0,
            "title": chat_title
        }]
    
    chat_member = [{
            "_id" : ObjectId(),
            "chatId" : ObjectId(chat_id),
            "user": {
                "email": data['user']["email"],
                **({"fname": data['user']["fname"]} if "fname" in data['user'] else {}),
                **({"lname": data['user']["lname"]} if "lname" in data['user'] else {}),
                **({"profile": data['user']["profile"]} if "profile" in data['user'] else {}),
                "id": ObjectId(data['user']["id"])
            },
            "brain": {
                        "title": config["brain_title"],
                        "slug": config["brain_slug"],
                        "id": ObjectId(config["brain_id"])
                    },
            "importId":import_id,
            "isFavourite" : False,
            "isNewChat" : True,
            **({"invitedBy": data['invitedBy']} if 'invitedBy' in data else {}),
            **({"teamId": data['teamId']} if 'teamId' in data else {}),
            "createdAt" : current_datetime,
            "updatedAt" : current_datetime,
            "__v" : 0,
            "title" : chat_title
        }for data in user_data]


    # Use the Dev database client
    # mongo_client = MongoClient(DEV_DB_URL)
    # db = mongo_client["weam-dev-01"]

    # Use the local database client

    chat_collection = db_instance.get_collection("chat")
    chat_member_collection = db_instance.get_collection("chatmember")

    try:
        chat_collection.insert_many(chat)
        print("Chat Data inserted successfully!:", chat_id)
        chat_member_collection.insert_many(chat_member)
    except Exception as e:
        print(f"Error inserting data: {e}")
    
    return chat_id