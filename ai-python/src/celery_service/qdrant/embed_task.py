from fastapi import HTTPException
from src.celery_service.celery_worker import celery_app
from typing import List
import os
from src.embedder.embedder_map.embed_model_mapping import  qdrant_text_embedder
from src.embedder.openai_embedder.qdrant_node import NodeTextEmbedderQdrant
from src.embedder.chunk_map.chunking_funmap import map_functions
from src.embedder.helper_pack.utils_embedder import metadata_map
from src.embedder.spliter.langchain_spliter import spliter_map
from src.celery_service.mongodb.task_status import log_task_status
from src.logger.default_logger import logger
from src.crypto_hub.services.openai.embedding_api_key_decryption import EmbeddingAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.openai.cost_embedding.count_embed_tokens import CostEmbedding
from src.celery_service.qdrant.localstack_backup import upload_df_embed_to_localstack,upload_df_embed_to_s3,upload_df_embed_to_minio
from src.chatflow_langchain.repositories.file_repository import FileRepository
from src.db.qdrant_config import qdrant_url,qdrant_client
from qdrant_client.models import PointStruct
CHUNK_SIZE = 400
embedding_apikey_decrypt_service = EmbeddingAPIKeyDecryptionHandler()


store_bucket_dict={
    "LOCALSTACK": upload_df_embed_to_localstack,
    "AWS_S3":upload_df_embed_to_s3,
    "MINIO":upload_df_embed_to_minio
}

# Background task for token cost tracking
@celery_app.task
def track_embedding_cost(chunk_texts: List[str], model_name: str, file_id: str, file_collection: str):
    try:
        cost_embed = CostEmbedding()
        file_repo = FileRepository()
        file_repo.initialization(file_id, file_collection)

        token_data = cost_embed.calculate_cost_for_embedding(chunk_texts, model_name)
        file_repo.update_tokens(token_data)

        logger.info("Token cost tracking completed", extra={"tags": {"task": "track_embedding_cost"}})
    except Exception as e:
        logger.warning(f"Cost tracking failed: {e}")

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 5},
    queue="openai_embedding"
)
def data_preparation(self,text_data: str, chunk_maptype: str,**kwargs) -> List[str]:
    """
    Prepares data by chunking the given text data and applying metadata to each chunk.

    Parameters:
    - text_data (str): The text data to be chunked.
    - chunk_maptype (str): The type of chunking function to use, must be a key in `map_functions` dict.
    - spliter (str): The function name to split text data into chunks. Defaults to `custom_text_splitter`.
    - tag (str): An optional tag to be added to each chunk's metadata. Defaults to "default".
    - meta_addfun (str): The function name to apply additional metadata to each chunk. Defaults to `addition_metadata`.

    Returns:
    - List[str]: The list of chunked data with metadata applied.

    Raises:
    - KeyError: If `chunk_maptype` is not found in the `map_functions` dictionary.
    """
    try:
        fun_meta=metadata_map.get("addition_metadata_qdrant")
        spliter_fun=spliter_map.get(kwargs.get("file_type"))
        chunking_function = map_functions.get(chunk_maptype)
        brain_id = kwargs.get("brain_id", None)

        chunked_data = chunking_function(text_data, spliter_fun)
        chunked_data = fun_meta(chunked_data, kwargs.get("tag"), id=kwargs.get("id"),file_name=kwargs.get("file_name"),brain_id=brain_id)  ## control vector embedding
        logger.info(
            "Task successfully executed",
            extra={"tags": {"task_function": "data_preparation"}}
        )
    except Exception as e:
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"task_function": "data_preparation"}}
        )
        raise HTTPException(status_code=400, detail=str(e))
    return chunked_data


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 5},
    queue="openai_embedding"
)
def start_embedding_openai(
    self,
    chunked_data: List = None,
    node_text_embedder: str = None,
    **kwargs
):
    """
    Embeds the given chunked data using the specified embedding instance.

    Parameters:
    - chunked_data (dict): The chunked data to be embedded.
    - node_text_embedder (str): The identifier for the embedding instance.

    Keyword Arguments:
    - api_key_id (str): API key identifier, defaults to '1'.
    - model_name (str): Model name for the embedding.
    - dimensions (int): Number of dimensions for the embedding, defaults to 1536.

    Returns:
    - list: The result of the embedding process.

    Raises:
    - HTTPException: Raises an error with status code 500 if embedding fails.
    """
    try:
        log_task_status.apply_async(kwargs={
            '_id': kwargs.get("id"),
            'status': 'STARTED',
            'task_progress': 'OPENAI_EMBEDDING',
            'collection': 'file'
        })

        embedder_class = qdrant_text_embedder.get(node_text_embedder, NodeTextEmbedderQdrant)

        api_key_id = kwargs.get("api_key_id", None)

        embedding_apikey_decrypt_service.initialization(api_key_id, kwargs.get('companymodel', 'companymodel'))

        embedder_instance = embedder_class(
            model_name=embedding_apikey_decrypt_service.model_name,
            api_key=embedding_apikey_decrypt_service.decrypt(),
            dimensions=embedding_apikey_decrypt_service.dimensions
        )
        chunk_list = [chunk['payload']['text'] for chunk in chunked_data]
        track_embedding_cost.delay(chunk_list, embedding_apikey_decrypt_service.model_name, kwargs.get("id"), kwargs.get("file_collection"))

        company_id=kwargs.get("company_id")
        qdrant_client_instance = qdrant_client
        bucket_type = os.environ.get("BUCKET_TYPE", "MINIO")

       

        # Process chunks in batches asynchronously
        def embed_and_upload():
            for i in range(0, len(chunked_data), CHUNK_SIZE):
                chunk_batch = chunked_data[i:i + CHUNK_SIZE]
                logger.info(
                    f"Processing batch {i // CHUNK_SIZE + 1} of {((len(chunked_data) - 1) // CHUNK_SIZE) + 1}",
                    extra={
                        "tags": {
                            "task_function": "start_embedding_openai",
                            "batch_start_index": i,
                            "batch_end_index": min(i + CHUNK_SIZE, len(chunked_data)),
                            "total_chunks": len(chunked_data)
                        }
                    }
                )
                result =  embedder_instance(node_batch=chunk_batch)
                vector_nodes = result.get("embedded_nodes", [])
                if vector_nodes:
                    s3_key = f"{kwargs.get('company_id')}/{kwargs.get('namespace')}/{kwargs.get('tag')}_{i}.parquet"
                    store_bucket_dict[bucket_type].apply_async(kwargs={'data_list': vector_nodes, 's3_key': s3_key})
                    vector_nodes= [PointStruct(id=node['id'], vector=node['vector'], payload=node['payload']) for node in vector_nodes]
                    qdrant_client_instance.upsert(collection_name=company_id,points=vector_nodes)

        def new_func():
            logger.info()

        def new_func():
            logger.info()

        # Run the full batch embedding in one async loop
        embed_and_upload()
   
        logger.info(
            "Task successfully executed",
            extra={"tags": {"task_function": "start_embedding_openai"}}
        )
        return {
            "task": "embedding_completed",
            "chunks_processed": len(chunked_data),
            "model_used": embedding_apikey_decrypt_service.model_name,
            "bucket_type": bucket_type,
            "company_id": company_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"task_function": "start_embedding_openai"}}
        )
        raise HTTPException(status_code=400, detail=str(e))
    finally:
         for var in ['embedder_instance', 'chunked_data', 'chunk_list', 'cost_embed', 'file_repo']:
            if var in locals():
                del locals()[var]

