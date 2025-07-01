from fastapi import APIRouter, HTTPException, Request, Depends, status
from celery import chain
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.celery_worker_hub.extraction.tasks import extract_text_task
from src.gateway.schema.store_vector import OpenAIProcessTextRequest, StoreVectorResponse
from src.celery_service.openai.embed_task import data_preparation, start_embedding_openai
from src.celery_service.qdrant.insertion_task import insert_into_vector_db, on_task_success, on_task_failure
from src.celery_service.mongodb.task_status import log_task_status
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
from celery.result import AsyncResult
import redis

load_dotenv()

limit_vector = os.getenv("LIM_VECTORS", "5/minute")
delete_task_on_success = os.getenv("DELETE_TASK_ON_SUCCESS", "false").lower() == "true"

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

redis_url  = os.getenv("CELERY_BROKEN_URL")
redis_client = redis.StrictRedis.from_url(redis_url)

@router.post(
    "/openai-store-vector",
    summary="OpenAI Store Vector",
    description="Endpoint to process and store text data as vectors using OpenAI embedding and storage logic.",
    response_description="Task chain ID for tracking the process.",
    response_model=StoreVectorResponse,
)
# @limiter.limit(limit_vector)
async def process_and_store_text_openai(
    request: Request,
    openai_input: OpenAIProcessTextRequest,
    current_user=Depends(get_user_data)
) -> str:
    """
    Processes text data, embeds it with OpenAI, and stores the results in a vector database.

    This endpoint receives a request_node containing information about a text file, extracts the text content,
    prepares it for embedding, applies OpenAI embeddings, and stores the resulting vectors in a vector database.

    Parameters:
    - request_node (OpenAIProcessTextRequest): The OpenAIProcessTextRequest request_node object is Schema For Request Extraction,
      Embedding and Qdrant Vector Insertion:

    Returns:
    - str: The ID of the created task chain, allowing for later tracking and monitoring.

    Raises:
    - HTTPException: If there's an error during task chain initialization or processing.

    Task Workflow:
    1. Extracts text from the specified file.
    2. Prepares the text for embedding (e.g., chunking, metadata processing).
    3. Embeds the text using OpenAI.
    4. Inserts the embedded vectors into a Qdrant vector database.

    On successful task completion or failure, callbacks are triggered to handle subsequent processing.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/openai-store-vector")
    try:
        task_chain = chain(
            extract_text_task.s(
                file_url=openai_input.file_url,
                file_type=openai_input.file_type,
                source=openai_input.source,
                page_wise=str(openai_input.page_wise),
                tag=openai_input.tag,
                id=openai_input.id,
            ),
            data_preparation.s(
                chunk_maptype=openai_input.chunk_maptype,
                meta_addfun=openai_input.meta_addfun,
                spliter=openai_input.spliter,
                tag=openai_input.tag,
                id=openai_input.id,
                file_name=openai_input.file_name,
                file_type=openai_input.file_type,
            ),
            start_embedding_openai.s(
                node_text_embedder=openai_input.node_text_embedder,
                api_key_id=openai_input.api_key_id,
                model_name=openai_input.model_name,
                dimensions=openai_input.dimensions,
                tag=openai_input.tag,
                id=openai_input.id,
                companymodel=openai_input.companymodel,
                file_collection=openai_input.file
            ),
            insert_into_vector_db.s(
                environment=openai_input.environment,
                company_id=openai_input.company_id,
                namespace=openai_input.brain_id,
                vector_index=openai_input.vector_index,
                tag=openai_input.tag,
                id=openai_input.id,
                companypinecone=openai_input.companypinecone
            ),
        ).apply_async(
            link=on_task_success.s(tag=openai_input.tag, id=openai_input.id),
            link_error=on_task_failure.s(id=openai_input.id, tag=openai_input.tag),
        )
        task_chain_id = task_chain.id

        log_task_status.apply_async(
            kwargs={
                "_id": openai_input.id,
                "task_id": task_chain_id,
                "status": "PENDING",
                "task_progress": "QUEUE",
                "collection": "file",
            }
        )
        logger.info(
            "Data processed and stored",
            extra={"tags": {"endpoint": "/openai-store-vector"}}
        )
        final_result = task_chain.get()

        task_result = AsyncResult(task_chain_id)
        if task_result.state == 'FAILURE':
            exc = task_result.result
            raise Exception(f'Task failed with error: {exc}')        
        
        # if task_result.state == 'SUCCESS' and delete_task_on_success:
        #     delete_task_from_redis(redis_client, task_chain_id)           
        
        return StoreVectorResponse(task_chain_id=task_chain_id)
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/openai-store-vector",
                    "task_chain_id": task_chain_id,
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI
    except Exception as e:
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"endpoint": "/openai-store-vector"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

