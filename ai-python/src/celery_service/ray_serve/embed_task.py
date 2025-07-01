from fastapi import HTTPException
from src.celery_service.celery_worker import celery_app
from typing import List
from src.embedder.embedder_map.embed_model_mapping import pinenode_text_embedder
from src.embedder.ray_serve_embedder.pinecone_node import NodeTextEmbedderRayServe
from src.embedder.helper_pack.utils_embedder import get_default_key_url
from src.celery_service.mongodb.task_status import log_task_status
from src.logger.default_logger import logger


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 5},
    queue="openai_embedding"
)
def start_embedding_ray_serve(
    self,
    chunked_data: List = None,
    node_text_embedder: str = None,
    tag: str = None,
    **kwargs
):
    """
    Embeds the given chunked data using the specified embedding instance.

    Parameters:
    - chunked_data (dict): The chunked data to be embedded.
    - node_text_embedder (str): The identifier for the embedding instance.

    Keyword Arguments:
    - api_url_id (str): API key identifier, defaults to '1'.
    - model_name (str): Model name for the embedding.
    - dimensions (int): Number of dimensions for the embedding, defaults to 1536.

    Returns:
    - list: The result of the embedding process.

    Raises:
    - HTTPException: Raises an error with status code 500 if embedding fails.
    """
    try:
        log_task_status.apply_async(
            kwargs={
                '_id': kwargs.get("id"),
                'status': 'STARTED',
                'task_progress': 'OPENAI_EMBEDDING',
                'collection': 'file'
            }
        )
        embedder_class = pinenode_text_embedder.get(node_text_embedder, NodeTextEmbedderRayServe)
        api_url_id = kwargs.get("api_url_id", "1")
        model_name = kwargs.get("model_name")
        dimensions = kwargs.get("dimensions", 768)
        api_url = get_default_key_url(api_url_id=api_url_id)

        embedder_instance = embedder_class(model_name=model_name, api_url=api_url, dimensions=dimensions)
        embedded_nodes = embedder_instance(chunked_data)['embedded_nodes']
        logger.info(
            "Task successfully executed",
            extra={"tags": {"task_function": "start_embedding_ray_serve"}}
        )
        return embedded_nodes
    except Exception as e:
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"task_function": "start_embedding_ray_serve"}}
        )
        raise HTTPException(status_code=500, detail=str(e))

