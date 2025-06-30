from dotenv import load_dotenv
import os
from src.logger.default_logger import logger
import redis
from celery.result import AsyncResult

load_dotenv()

redis_url = os.environ.get("CELERY_BROKEN_URL")
redis_client = redis.StrictRedis.from_url(redis_url)
  
def check_redis_connection() -> bool:
    """
    Check if the Redis connection is established by sending a ping.
    Logs the connection attempt for task deletion and returns True if connected, False otherwise.
    """
    try:
        redis_client.ping()
        logger.info("Redis connection successful. Ready to delete tasks from Redis.")
        return True
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis connection failed. Unable to delete tasks from Redis: {e}")
        return False

def get_redis_key(task_id: str) -> str:
    """
    Helper function to construct Redis key for a task.
    """
    return f'celery-task-meta-{task_id}'

def check_task_exists(redis_client, task_id: str) -> bool:
    """
    Check if a task exists in Redis.
    """
    redis_key = get_redis_key(task_id)
    return redis_client.exists(redis_key)

def delete_task_from_redis(redis_client, task_id: str) -> bool:
    """
    Delete task metadata from Redis.
    """
    redis_key = get_redis_key(task_id)
    if redis_client.exists(redis_key):
        redis_client.delete(redis_key)
        logger.info(f"Task {task_id} successfully deleted from Redis.")
        return True
    else:
        logger.warning(f"Task {task_id} not found in Redis.")
        return False
    
def delete_all_success_tasks_in_redis():
    """
    Utility function to delete all Celery tasks with status 'SUCCESS' from Redis.
    """
    if not check_redis_connection():
        logger.error("Redis connection failed. Unable to proceed with task deletion.")
        return 
    try:
        task_keys = redis_client.keys("celery-task-meta-*")
        if not task_keys:
            logger.info("No task metadata found in Redis.")
            return {"message": "No task metadata found in Redis."}

        deleted_tasks = []
        for key in task_keys:
            task_id = key.decode('utf-8').replace("celery-task-meta-", "")
            task_result = AsyncResult(task_id)

            if task_result.state == 'SUCCESS':
                delete_task_from_redis(redis_client, task_id)
                deleted_tasks.append(task_id)

        if deleted_tasks:
            logger.info(f"Successfully deleted {len(deleted_tasks)} tasks with status 'SUCCESS'. Task IDs: {deleted_tasks}")
            return {
                "message": f"Successfully deleted {len(deleted_tasks)} tasks with status 'SUCCESS' from Redis.",
                "deleted_task_ids": deleted_tasks
            }
        else:
            logger.info("No tasks with status 'SUCCESS' were found in Redis for deletion.")
            return {"message": "No tasks with status 'SUCCESS' found in Redis."}

    except Exception as e:
        logger.error(f"An error occurred while deleting success tasks: {e}")
        raise Exception(f"Error deleting success tasks: {e}")
    


def get_default_header():
    return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        }