from fastapi import APIRouter, HTTPException, Request, Depends, status
from celery import chain
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.celery_worker_hub.extraction.tasks import extract_text_task
from src.gateway.schema.store_multiVector import StoreVectorResponse,OpenAIMultiVectorStore
from src.celery_service.openai.embed_task import data_preparation, start_embedding_openai
from src.celery_service.qdrant.insertion_task import insert_into_vector_db
from src.celery_service.mongodb.task_status import log_task_status
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import redis
from celery import chain, group
import gc
load_dotenv()

limit_vector = os.getenv("LIM_VECTORS", "5/minute")
delete_task_on_success = os.getenv("DELETE_TASK_ON_SUCCESS", "false").lower() == "true"

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

redis_url  = os.getenv("CELERY_BROKEN_URL")
redis_client = redis.StrictRedis.from_url(redis_url)

@router.post(
    "/openai-multi-store-vector",
    summary="OpenAI Multi Store Vector",
    description="Endpoint to process and store text data as vectors using OpenAI embedding and storage logic.",
    response_description="Task chain ID for tracking the process.",
    response_model=StoreVectorResponse,
)
# @limiter.limit(limit_vector)
async def process_and_store_text_openai(
    request: Request,
    openai_input: OpenAIMultiVectorStore,
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
    log_api_call("/openai-multi-store-vector")
    try:
        task_chains = []
        for input in openai_input.payload_list:
            task_chain = chain(
                extract_text_task.s(
                    file_url=input.file_url,
                    file_type=input.file_type,
                    source=input.source,
                    page_wise=str(input.page_wise),
                    tag=input.tag,
                    id=input.id,
                ),
                data_preparation.s(
                    chunk_maptype=openai_input.chunk_maptype,
                    meta_addfun=openai_input.meta_addfun,
                    spliter=openai_input.spliter,
                    tag=input.tag,
                    id=input.id,
                    file_name=input.file_name,
                    file_type=input.file_type,
                ),
                start_embedding_openai.s(
                    node_text_embedder=openai_input.node_text_embedder,
                    api_key_id=input.api_key_id,
                    model_name=openai_input.model_name,
                    dimensions=input.dimensions,
                    tag=input.tag,
                    id=input.id,
                    companymodel=openai_input.companymodel,
                    file_collection=openai_input.file
                ),
                insert_into_vector_db.s(
                    environment=openai_input.environment,
                    company_id=input.company_id,
                    namespace=input.brain_id,
                    vector_index=input.vector_index,
                    tag=input.tag,
                    id=input.id,
                    companypinecone=openai_input.companypinecone
                ),
            )
            task_chains.append(task_chain)

            # Log task status
            log_task_status.apply_async(
                kwargs={
                    "_id": input.id,
                    "task_id": task_chain.id,
                    "status": "PENDING",
                    "task_progress": "QUEUE",
                    "collection": "file",
                }
            )
            logger.info(
                "Data processing initiated for file",
                extra={"tags": {"endpoint": "/openai-multi-store-vector", "file_id": input.id}},
            )

        # Execute all chains as a group
        group_result = group(task_chains).apply_async()
        group_id = group_result.id

        # Wait for all chains to complete
        group_result.join()

        # Check for any failures
        if group_result.failed():
            failed_tasks = [res for res in group_result.results if res.state == 'FAILURE']
            errors = [res.result for res in failed_tasks]
            raise Exception(f"One or more tasks failed: {errors}")

        # Collect results for all chains
        # final_results = [res.get() for res in group_result.results]

        group_result.forget()
        group_result = None
        del task_chains
        task_chains = None
        gc.collect()

        logger.info("All files processed successfully.")
        return StoreVectorResponse(task_chain_id=group_id)         
        

    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/openai-multi-store-vector",
                    "task_chain_id": "task_chain_id",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI
    except Exception as e:
        if 'group_result' in locals():
            group_result.forget()
        
            # Clean up resources
            del task_chains
        gc.collect()
        
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"endpoint": "/openai-multi-store-vector"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))