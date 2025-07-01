# utils/vector_provider_chains.py


from src.celery_worker_hub.extraction.tasks import extract_text_task
from src.celery_service.qdrant.embed_task import (
    data_preparation,
    start_embedding_openai,

)
from src.celery_service.qdrant.insertion_task import insert_into_vector_db
VECTOR_DB_TASK_CHAINS = {
    "qdrant": {
        "extract": extract_text_task,
        "prepare": data_preparation,
        "embed": start_embedding_openai,
        "insert": insert_into_vector_db,

    
    },
    # Add more like "weaviate": {...}
}
