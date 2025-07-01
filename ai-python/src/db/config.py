from pymongo import MongoClient
import os
from typing import Dict, Any
from src.crypto_hub.utils.crypto_utils import decrypt_dict_data

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MongoDBClient(metaclass=Singleton):
    def __init__(self):
        # Read MongoDB credentials and host info from environment variables
        self.mongo_user = os.getenv('DB_USERNAME',None)
        self.mongo_password = os.getenv('DB_PASSWORD',None)
        self.mongo_host = os.getenv('DB_HOST', 'localhost')  # Default to localhost if not specified
        self.mongo_port = os.getenv('DB_PORT', '27017')  # Default to 27017 if not specified
        self.mongo_db_name = os.getenv('DB_DATABASE', 'customai')  # Default to 'mydatabase' if not specified
        self.mongo_db_connection=os.environ.get("DB_CONNECTION","mongodb")
        self.db=None
        # Construct the MongoDB URI
        uri=os.environ.get("MONOGODB_URI",None)
        if uri is None:
            if self.mongo_user and self.mongo_password:
                uri = f"{self.mongo_db_connection}://{self.mongo_user}:{self.mongo_password}@{self.mongo_host}"
            else:
                uri = f"{self.mongo_db_connection}://{self.mongo_host}:{self.mongo_port}/"

        # Initialize the MongoDB client

        self.client = MongoClient(uri)

    def get_database(self, db_name=None):
        if db_name is None:
            self.db=self.client[self.mongo_db_name]  # Default to 'mydatabase' if not specified
        else:
            self.db=self.client[db_name]
        return self.db
    
    def get_collection(self, collection_name, db_name=None):
        db = self.get_database(db_name)
        return db[collection_name]


def get_db_instance(db_name=None):
    """
    Function to get a MongoDB database instance.
    
    :param db_name: Optional. Specify the database name if you want to connect to a specific database other than the default.
    :return: MongoDB Database object
    """
    mongo_client = MongoDBClient()
    return mongo_client.get_database(db_name)

def get_field_by_name(collection_name=None, name=None, field_name=None, db_name=None):
    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection(collection_name, db_name)
    projection = {field_name: 1, "_id": 0}

    document = collection.find_one({"code": name}, projection)

    return document.get(field_name) if document else {}

def get_records_dynamic(collection_name: str, field_name: str = None, field_value=None, get_all: bool = False, db_name: str = None):
    """
    Fetch documents from a MongoDB collection dynamically.

    Parameters:
    - collection_name (str): Name of the MongoDB collection to query.
    - field_name (str, optional): Field to filter by (supports dot notation for nested fields).
    - field_value (any, optional): Value to match for the given field_name.
    - db_name (str, optional): Name of the MongoDB database. If None, uses the default.
    - get_all (bool): If True, returns all matching documents. If False, returns only the first match.

    Returns:
    - A single document (dict) if get_all is False and field_name/field_value are provided.
    - A list of documents (list[dict]) in all other cases.
    """
    
    # Initialize MongoDB client and target collection
    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection(collection_name, db_name)

    # Construct query only if field_name and field_value are provided
    query = {field_name: field_value} if field_name and field_value is not None else {}

    # Return one document or all depending on get_all flag
    if field_name and field_value is not None and not get_all:
        return collection.find_one(query)
    else:
        return list(collection.find(query))

db_instance= get_db_instance()
# db_field_value = get_field_by_name()
# # Example usage
# mongo_client = MongoDBClient()
# db = mongo_client.get_database()

def get_decrypted_details(collection_name: str, code_name: str, field_name: str = "details", db_name: str = None) -> Dict[str, Any]:
    """
    Fetch and decrypt a dictionary field from MongoDB.

    Args:
        collection_name (str): Name of the collection to fetch from.
        code_name (str): Value of the 'code' field to locate the document.
        field_name (str): Field name to decrypt (default: 'details').
        db_name (str, optional): Database name (defaults to default DB).

    Returns:
        Dict[str, Any]: Decrypted dictionary or empty dict on failure.
    """
    raw_encrypted = get_field_by_name(
        collection_name=collection_name,
        name=code_name,
        field_name=field_name,
        db_name=db_name
    )
    return decrypt_dict_data(raw_encrypted)
