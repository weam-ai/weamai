from qdrant_client import QdrantClient
from qdrant_client import QdrantClient, models
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import KeywordIndexParams
from src.vector_store.qdrant.langchain_lib.index_config import VECTOR_DISTANCE,VECTOR_SIZE, HNSW_CONFIG,INDEX_FIELDS

class QdrantSetup:
    def __init__(self, client: QdrantClient):
        self.client = client
        self.COLLECTION_NAME=None

    def initialization(self,company_id:str=None):
        print("Starting Qdrant setup and S3 upload...")
        self.COLLECTION_NAME=company_id

        if not self.client.collection_exists(self.COLLECTION_NAME):
            self._create_collection()
            self._create_indexes()
            return f"Collection '{self.COLLECTION_NAME}' created with vector size {VECTOR_SIZE}"
        else:
            return f"Collection '{self.COLLECTION_NAME}' already exists. Skipping creation."

    def _create_collection(self):
        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=VECTOR_DISTANCE),
            hnsw_config=models.HnswConfigDiff(**HNSW_CONFIG),
        )

    def _create_indexes(self):
        for field_name, field_opts in INDEX_FIELDS.items():
            self.client.create_payload_index(
                collection_name=self.COLLECTION_NAME,
                field_name=field_name,
                field_schema=models.KeywordIndexParams(**field_opts),
            )
