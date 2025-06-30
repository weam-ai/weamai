from fastapi import APIRouter, Request, HTTPException, Depends, status
from celery import chain
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.celery_service.ray_serve.embed_task import start_embedding_ray_serve
from src.celery_worker_hub.extraction.tasks import extract_text_task
from src.gateway.schema.store_vector import RayServeEmbedProcessTextRequest, StoreVectorResponse
from src.celery_service.openai.embed_task import data_preparation
from src.celery_service.qdrant.insertion_task import insert_into_vector_db, on_task_success,on_task_failure
from src.celery_service.mongodb.task_status import log_task_status
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_ray = os.getenv("LIM_RAY", "5/minute")

@router.post(
    "/custom-store-vector",
    summary="Custom Store Vector",
    description="Endpoint to process and store text data as vectors using custom embedding and storage logic.",
    response_description="Task chain ID for tracking the process.",
    response_model=StoreVectorResponse,
)
# @limiter.limit(limit_ray)
async def process_and_custom_store_text(
    request: Request,
    embedding_input: RayServeEmbedProcessTextRequest,
    current_user=Depends(get_user_data)
) -> str:
    """
    Custom Store Vector.

    This endpoint processes and stores text data as vectors using custom embedding and storage logic.

    Args:
        request (Request): The incoming HTTP request.
        embedding_input (RayServeEmbedProcessTextRequest): Input data for processing and storing text as vectors.

    Returns:
        str: The task chain ID for tracking the process.

    Raises:
        HTTPException: If there is an error processing or storing the text.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/custom-store-vector")
    try:    
            task_chain = chain(
                extract_text_task.s(
                    file_url=embedding_input.file_url,
                    file_type=embedding_input.file_type,
                    source=embedding_input.source,
                    page_wise=str(embedding_input.page_wise),
                    tag=embedding_input.tag,
                    id=embedding_input.id,
                ),
                data_preparation.s(
                    chunk_maptype=embedding_input.chunk_maptype,
                    meta_addfun=embedding_input.meta_addfun,
                    spliter=embedding_input.spliter,
                    tag=embedding_input.tag,
                    id=embedding_input.id,
                ),
                start_embedding_ray_serve.s(
                    node_text_embedder=embedding_input.node_text_embedder,
                    api_url_id=embedding_input.api_url_id,
                    model_name=embedding_input.model_name,
                    dimensions=embedding_input.dimensions,
                    tag=embedding_input.tag,
                    id=embedding_input.id,
                ),
                insert_into_vector_db.s(
                    environment=embedding_input.environment,
                    pinecone_apikey_id=embedding_input.pinecone_apikey_id,
                    namespace=embedding_input.brain_id,
                    vector_index=embedding_input.vector_index,
                    tag=embedding_input.tag,
                    id=embedding_input.id,
                ),
            ).apply_async(
                link=on_task_success.s(tag=embedding_input.tag, id=embedding_input.id),
                link_error=on_task_failure.s(id=embedding_input.id, tag=embedding_input.tag),
            )
            task_chain_id = task_chain.id

            log_task_status.apply_async(
                kwargs={
                    "_id": embedding_input.id,
                    "task_id": task_chain_id,
                    "status": "PENDING",
                    "task_progress": "QUEUE",
                    "collection": "file",
                }
            )
            logger.info(
                "Data processed and stored",
                extra={"tags": {"endpoint": "/custom-store-vector"}}
            )
            return StoreVectorResponse(task_chain_id=task_chain_id)
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/custom-store-vector",
                    "task_chain_id": task_chain_id,
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI
    except Exception as e:
        logger.error(
            f"Error executing Custom Ray Store Vector API: {e}",
            extra={"tags": {"endpoint": "/custom-store-vector"}}
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
