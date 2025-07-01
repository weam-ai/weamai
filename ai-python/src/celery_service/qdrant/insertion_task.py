from src.celery_service.celery_worker import celery_app
from fastapi import HTTPException
import redis
from typing import List
from src.celery_service.mongodb.task_status import log_task_status
from src.logger.default_logger import logger
from src.celery_service.utils import delete_all_success_tasks_in_redis
from src.celery_service.qdrant.localstack_backup import upload_df_embed_to_localstack,upload_df_embed_to_s3,upload_df_embed_to_minio
from src.chatflow_langchain.repositories.settings_repository import SettingRepository
from qdrant_client import QdrantClient
from src.db.qdrant_config import qdrant_url,qdrant_client
from qdrant_client.models import PointStruct
import os
from dotenv import load_dotenv
load_dotenv()
API_CALL_COUNT_KEY_REDIS = os.environ.get("API_CALL_COUNT_KEY_REDIS","redis_api_call_count")
redis_url = os.environ.get("CELERY_BROKEN_URL")
redis_client = redis.StrictRedis.from_url(redis_url)
delete_task_on_success = os.getenv("DELETE_TASK_ON_SUCCESS", "false").lower() == "true"

store_bucket_dict={
    "LOCALSTACK": upload_df_embed_to_localstack,
    "AWS_S3":upload_df_embed_to_s3,
    "MINIO":upload_df_embed_to_minio
}

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 0, 'countdown': 0},queue="qdrant_insertion")
def insert_into_vector_db(self,vector_nodes: List, **kwargs):
    """
    Inserts the given vector nodes into a vector database.

    Parameters:
    - vector_nodes (List): The list of vector nodes to be inserted.
    
    Keyword Arguments:
    - environment (str): Specifies the environment for Qdrant.
    - vector_index (str): Name of the vector index in the database.
    - namespace (str): Namespace for indexing.

    Returns:
    - str: Confirmation message indicating successful insertion.

    Raises:
    - Exception: If an error occurs during the insertion process.
    """
    try:
        log_task_status.apply_async(kwargs={'_id': kwargs.get("id"),'status': 
                                        'STARTED','task_progress': 'QDRANT_INSERTION',
                                        'collection': 'file'
                                })
        company_id=kwargs.get("company_id")
        s3_file_key = f"{kwargs.get('company_id')}/{kwargs.get('namespace')}/{kwargs.get('tag')}.parquet"
        qdrant_client_instance = qdrant_client

        bucket_type = os.environ.get("BUCKET_TYPE", "MINIO")

        store_bucket_dict[bucket_type].apply_async(kwargs={'data_list': vector_nodes, 's3_key': s3_file_key})
        vector_nodes= [PointStruct(id=node['id'], vector=node['vector'], payload=node['payload']) for node in vector_nodes]
        
        
    

        qdrant_client_instance.upsert(collection_name=company_id,points=vector_nodes)
        logger.info(
            "Task successfully executed",
            extra={"tags": {"task_function": "insert_into_vector_db"}}
        )
        return "Inserted into DB successfully"
    except Exception as e:
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"task_function": "insert_into_vector_db"}}
        )
        raise HTTPException(status_code=400, detail=f"Failed to executing task: {e}")
    finally:
         # Optimized cleanup: iterate over a list of variables and delete them if defined.
        for var in ['initializer',"vector_nodes","api_key","s3_file_key"]:
            if var in locals():
                del locals()[var]


# Define callback functions
# Celery tasks to handle task outcomes (failure and success).
@celery_app.task
def on_task_failure(*args, **extras):
    """
    Handle the failure of a Celery task.

    This function is triggered when a Celery task fails.
    It logs the failure and sends relevant information for further processing.

    Args:
        args: Positional arguments passed to the function.
        extras (dict): A dictionary containing extra information about the task.
                       Expected keys include 'tag' for task identification and 'id' for logging.
    """
    try:
        # Output basic information about the failure
        logger.error(f"Task '{extras.get('tag')}' raised an exception:")
        logger.error("Additional Information: %s", extras)
        logger.error("Arguments: %s", args)

        # Log the failure status using another Celery task
        log_task_status.apply_async(
            kwargs={
                '_id': extras.get("id"),  # ID for identifying the failed task
                'status': 'FAILURE',  # Status indicating failure
                'task_progress': 'FAILED',  # Description of the task's progress
                'collection': 'file'  # The collection to which the task status is logged
            })

    except Exception as e:
        logger.error(f"Error in handling task success for task: {e}")
    finally:
        try:
            # Ensure Redis API call count is decremented only if positive
            current_count = redis_client.get(API_CALL_COUNT_KEY_REDIS)
            if current_count and int(current_count) > 0:
                updated_count = redis_client.decr(API_CALL_COUNT_KEY_REDIS)
                logger.info(f"Decremented API call count after task completion: {updated_count}")
            else:
                logger.warning("API call count is already zero or missing, no decrement performed.")
        except Exception as e:
            logger.error(f"Error while decrementing API call count: {e}")

@celery_app.task
def on_task_success(message, tag: str = None, id: str = None):
    """
    Handle the success of a Celery task.

    This function is triggered when a Celery task successfully completes.
    It logs the success and triggers any additional processing.

    Args:
        message (str): A message containing information about the task success.
        tag (str): An optional tag for identifying the task.
        id (str): An optional ID used for logging the task status.
    """
    try:
        # Output basic information about the success
        logger.info("Message: %s", message)
        logger.info(f"Task '{tag}' successfully completed")

        # Log the success status using another Celery task
        log_task_status.apply_async(
            kwargs={
                '_id': id,  # ID for identifying the successful task
                'status': 'SUCCESS',  # Status indicating success
                'task_progress': 'COMPLETED',  # Description of the task's progress
                'collection': 'file'  # The collection to which the task status is logged
            })
    except Exception as e:
        # Handle any errors that occur during the success handling
        logger.error(f"Error in handling task success for task '{tag}': {e}")

    finally:
        if delete_task_on_success:
            delete_all_success_tasks_in_redis()
        try:
            # Ensure Redis API call count is decremented only if positive
            current_count = redis_client.get(API_CALL_COUNT_KEY_REDIS)
            if current_count and int(current_count) > 0:
                updated_count = redis_client.decr(API_CALL_COUNT_KEY_REDIS)
                logger.info(f"Decremented API call count after task completion: {updated_count}")
            else:
                logger.warning("API call count is already zero or missing, no decrement performed.")
        except Exception as e:
            logger.error(f"Error while decrementing API call count: {e}")