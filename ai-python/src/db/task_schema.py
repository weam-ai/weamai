# JSON schema definition
task_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["task_id", "status"],
        "properties": {
            "task_id": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "status": {
                "bsonType": "string",
                "enum": ["FAILURE", "RECEIVED", "PENDING", "RETRY", "REVOKED", "STARTED", "SUCCESS"],
                "description": "must be a string from the specified enumeration and is required"
            },
            "progress": {
                "bsonType": "string",
                "enum": ["OPENAI_EMBEDDING", "QDRANT_INSERTION", "QUEUE", "FAILED", "COMPLETED", "EXTRACTION"],
                "description": "must be a string from the specified enumeration and is required"
            }
        }
    }
}
