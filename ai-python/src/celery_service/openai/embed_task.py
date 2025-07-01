from fastapi import HTTPException
from src.celery_service.celery_worker import celery_app
from typing import List
from src.embedder.embedder_map.embed_model_mapping import pinenode_text_embedder
from src.embedder.openai_embedder.pincone_node import NodeTextEmbedderOpenAI
from src.embedder.chunk_map.chunking_funmap import map_functions
from src.embedder.helper_pack.utils_embedder import metadata_map
from src.embedder.spliter.langchain_spliter import spliter_map
from src.celery_service.mongodb.task_status import log_task_status
from src.logger.default_logger import logger
from src.crypto_hub.services.openai.embedding_api_key_decryption import EmbeddingAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.openai.cost_embedding.count_embed_tokens import CostEmbedding
from src.chatflow_langchain.repositories.file_repository import FileRepository
embedding_apikey_decrypt_service = EmbeddingAPIKeyDecryptionHandler()


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
        fun_meta=metadata_map.get(kwargs.get("meta_addfun"))
        spliter_fun=spliter_map.get(kwargs.get("file_type"))
        chunking_function = map_functions.get(chunk_maptype)

        chunked_data = chunking_function(text_data, spliter_fun)
        chunked_data = fun_meta(chunked_data, kwargs.get("tag"), id=kwargs.get("id"),file_name=kwargs.get("file_name"))  ## control vector embedding
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
    tag:str=None,
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

        embedder_class = pinenode_text_embedder.get(node_text_embedder, NodeTextEmbedderOpenAI)

        api_key_id = kwargs.get("api_key_id", None)

        embedding_apikey_decrypt_service.initialization(api_key_id, kwargs.get('companymodel', 'companymodel'))

        embedder_instance = embedder_class(
            model_name=embedding_apikey_decrypt_service.model_name,
            api_key=embedding_apikey_decrypt_service.decrypt(),
            dimensions=embedding_apikey_decrypt_service.dimensions
        )
        chunk_list = [chunk['metadata']['text'] for chunk in chunked_data]
        cost_embed = CostEmbedding()
        file_repo = FileRepository()
        file_repo.initialization(file_id=kwargs.get('id'),collection_name=kwargs.get('file_collection'))
        token_data = cost_embed.calculate_cost_for_embedding(chunk_list,embedding_apikey_decrypt_service.model_name)
        file_repo.update_tokens(token_data)
        embedded_nodes = embedder_instance(chunked_data)['embedded_nodes']
   
        logger.info(
            "Task successfully executed",
            extra={"tags": {"task_function": "start_embedding_openai"}}
        )
        return embedded_nodes
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

