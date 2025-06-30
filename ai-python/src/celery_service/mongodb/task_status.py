from celery import shared_task
from bson.objectid import ObjectId
from src.db.config import db_instance
from src.logger.default_logger import logger

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 0}, queue='log_task')
def log_task_status(self, _id: str = None, task_id: str = None, status: str = None, task_progress: str = "QUEUE", collection="file"):
    """
    Update or insert a task's status in a MongoDB collection.
    
    :param _id: The ID of the document to update (ObjectId).
    :param task_id: The unique identifier for the task being updated.
    :param status: The new status to set.
    :param task_progress: The progress of the task (default is "QUEUE").
    :param collection: The name of the MongoDB collection to update.
    """
    try:
        # Initialize the MongoDB collection
        collection = db_instance.get_collection(collection)
        
        # Define the query to check for the specified document using the provided _id
        if task_id is None:
            query = {"_id": ObjectId(_id)}
            
            # Define the update operation to change the task's status and progress
            update = {
                "$set": {
                    "tasks.status": status,
                    "tasks.progress": task_progress
                }
            }
            
            # Execute the update operation on the collection
            result = collection.update_one(query, update)
            logger.info(
            "Existing document was updated",
            extra={"tags": {"task_function": "log_task_status"}}
            )

          
        else:
            # If no document was found with the given _id, insert a new one
            upsert_query = {"_id": ObjectId(_id)}
            upsert_update = {
                "$set": {
                    "tasks": {
                        "task_id": task_id,
                        "status": status,
                        "progress": task_progress
                    }
                }
            }
            
            # Execute the upsert operation
            collection.update_one(upsert_query, upsert_update)

            logger.info("A new document was inserted.",
            extra={"tags": {"task_function": "log_task_status"}}
            )
    except Exception as e:
        # Raise an exception with a custom error message for better error handling
        raise Exception(f"log_task_status: An error occurred - {str(e)}")