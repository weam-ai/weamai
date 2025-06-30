# src/qdrant/index_config.py

from qdrant_client.http.models import Distance


VECTOR_SIZE = 1536  # Size of the vector embeddings, adjust as per your model
VECTOR_DISTANCE = Distance.COSINE

# Index field definitions
INDEX_FIELDS = {
    "brain_id": {
        "type": "keyword",
        "is_tenant": True
    },
    "tag": {
        "type": "keyword",
        "is_tenant": False
    }
}

# Optional: HNSW config
HNSW_CONFIG = {
    "payload_m": 16,
    "m": 0
}
