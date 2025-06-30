import redis, os, json
from dotenv import load_dotenv
from src.celery_worker_hub.import_worker.celery_app import celery_app
from src.logger.default_logger import logger

load_dotenv()
# Set the TTL value for failed tasks
RESULT_EXPIRE_TIME = 14400
FLAG_TIME = 600


@celery_app.task
def update_failed_tasks_ttl():
    """
    Extends the TTL (Time-to-Live) for failed Celery tasks stored in Redis.

    This function connects to a Redis server and retrieves all keys matching the
    pattern 'celery-task-meta-*', which corresponds to Celery task metadata. For each
    task, it checks if the task status is 'FAILURE' and if the TTL has not been extended
    yet (determined by the absence of the 'ttl_extended' flag in the task's hash).

    If the conditions are met, the TTL for the task metadata and the task hash is
    extended to a new value. The new TTL value is determined by the environment variable
    'RESULT_EXPIRE_TIME' or a default constant `RESULT_EXPIRE_TIME` if the environment
    variable is not set. The hash key's TTL is further extended by an additional time
    specified by the environment variable 'FLAG_TIME' or a default constant `FLAG_TIME`.

    Any exceptions encountered during the process are caught and logged to the console.

    Usage:
        Call this function as a periodic Celery task to ensure that failed tasks' metadata
        persists for a longer duration for debugging or auditing purposes.

    Raises:
        Exception: Logs any exception that occurs during Redis operations or TTL updates.

    Dependencies:
        - Redis server accessible at host 'redis' and port 6379.
        - Environment variables 'RESULT_EXPIRE_TIME' and 'FLAG_TIME' for custom TTL values.
        - Redis keys with the pattern 'celery-task-meta-*' representing Celery task metadata.
        - JSON encoded task data stored in Redis.
    """
    try:
        redis_client = redis.StrictRedis(host=os.environ.get("REDIS_URI","redis"), port=os.environ.get("REDIS_PORT",6379), db=int(os.environ.get("DB_NUMBER","7")))
        logger.info("Connected to Redis successfully.")

        jobs = redis_client.keys(pattern='celery-task-meta-*')
        logger.info(f"Found {len(jobs)} task(s) in Redis.")

        for job_key in jobs:
            job_info = json.loads(redis_client.get(job_key))
            logger.debug(f"Processing job key: {job_key}, info: {job_info}")

            if job_info.get('status') == 'FAILURE' and not redis_client.hget(job_info.get('task_id'), 'ttl_extended'):
                new_ttl = int(os.environ.get('RESULT_EXPIRE_TIME', RESULT_EXPIRE_TIME))
                redis_client.expire(job_key, new_ttl)
                logger.info(f"Extended TTL for job key: {job_key} by {new_ttl} seconds.")

                redis_client.hset(job_info.get('task_id'), 'ttl_extended', 1)
                redis_client.expire(job_info.get('task_id'), new_ttl + int(os.environ.get('FLAG_TIME', FLAG_TIME)))
                logger.info(f"Updated task '{job_info.get('task_id')}' to mark TTL as extended.")
                
    except Exception as e:
        logger.error(
            f"An error occurred: {e}",
            extra={"tags": {"task_function": "update_failed_tasks_ttl"}}
        )
