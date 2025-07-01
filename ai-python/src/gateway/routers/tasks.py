from fastapi import APIRouter, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from src.gateway.jwt_decode import get_user_data
from src.gateway.utils import log_api_call
import redis
from src.celery_service.utils import check_task_exists,delete_task_from_redis
from src.logger.default_logger import logger
import json
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()

redis_url  = os.getenv("CELERY_BROKEN_URL")
redis_client = redis.StrictRedis.from_url(redis_url)

@router.post(
    "/check-status",
    summary="Check Task Status",
    description="Endpoint to check the status of a task execution.",
    response_description="Response message containing the task status."
)
async def check_task_status(task_id: str = Form(...), current_user=Depends(get_user_data)):
    """
    Check Task Status.

    This endpoint allows users to check the status of a task execution.

    Args:
        task_id (str, Form): The unique identifier of the task.

    Returns:
        JSONResponse: A response message containing the task status.

    Raises:
        HTTPException: If there is an error while checking the task status.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/check-status")
    try:
        res = AsyncResult(task_id)
        if res.ready():
            if res.failed():
                return JSONResponse(content={
                    "status": "failed",
                    "reason": "Chain Task execution failed. Specific reason can be added based on task exception."
                }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                result = res.get(timeout=4.0)  # Adjust the timeout as necessary
                if 'error' in result:
                    return JSONResponse(content={
                        "status": "completed",
                        "result": result,
                        "message": "Completed with errors"
                    }, status_code=200)
                else:
                    return JSONResponse(content={"status": "completed", "result": result}, status_code=200)
        else:
            return JSONResponse(content={"status": "pending"}, status_code=202)
    except Exception as e:
        response_content = {"status": "error", "reason": str(e)}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response_content)


@router.get("/check-task-status/{task_id}")
async def check_redis_task_status(task_id: str):
    """
    Endpoint to check the status of a task and delete it from Redis if successful.
    """
    try:
        task_result = AsyncResult(task_id)
        # redis_key = get_redis_key(task_id)
        task_status = check_task_exists(redis_client, task_id)

        if task_status:
            logger.info(f"Task {task_id} exists in Redis.")
        else:
            logger.info(f"Task {task_id} does not exist in Redis.")

        if task_result.state == 'FAILURE':
            exc = task_result.result
            logger.error(f"Task {task_id} failed with error: {exc}")
            return {"task_id": task_id, "task_state": "FAILURE", "error": str(exc)}
        elif task_result.state == 'SUCCESS':
            exc = task_result.result
            return {"task_id": task_id, "task_state": "SUCCESS", "result": exc}
        else:
            logger.info(f"Task {task_id} is in state: {task_result.state}")
            return {"task_id": task_id, "task_state": task_result.state}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get-all-redis-data")
async def get_all_redis_data():
    """
    Endpoint to retrieve all Celery task metadata from Redis.
    """
    try:
        redis_client.ping()  # Test the connection
        task_keys = redis_client.keys("celery-task-meta-*")
        all_data = {}

        for task_key in task_keys:
            key = task_key.decode("utf-8")
            value = redis_client.get(task_key).decode("utf-8")
            all_data[key] = json.loads(value)

        response = {
            "total_count": len(all_data),
            "tasks": all_data
        }

        return response

    except redis.ConnectionError:
        logger.error("Failed to connect to Redis.")
        raise HTTPException(status_code=500, detail="Failed to connect to Redis.")
    except Exception as e:
        logger.error(f"Error retrieving data from Redis: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving data from Redis.")


@router.delete("/delete-task/{task_id}")
async def delete_task(task_id: str):
    """
    Endpoint to delete task metadata from Redis based on task ID.
    """
    try:
        task_delete = delete_task_from_redis(redis_client, task_id)
        if task_delete:
            return {"task_id": task_id, "message": "Task successfully deleted from Redis."}
        else:
            return {"task_id": task_id, "message": "Task not found in Redis."}

    except Exception as e:
        logger.error(f"An error occurred while deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting task {task_id}: {e}")


@router.delete("/delete-all-success-tasks")
async def delete_all_success_tasks():
    """
    Endpoint to delete all Celery tasks with status 'SUCCESS' from Redis.
    """
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
            return {
                "message": f"Successfully deleted {len(deleted_tasks)} tasks with status 'SUCCESS' from Redis.",
                "deleted_task_ids": deleted_tasks
            }
        else:
            return {"message": "No tasks with status 'SUCCESS' found in Redis."}

    except Exception as e:
        logger.error(f"An error occurred while deleting success tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting success tasks: {e}")