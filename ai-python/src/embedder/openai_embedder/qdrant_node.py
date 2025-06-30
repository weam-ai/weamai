from typing import List, Dict, Any
from langchain_community.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient

from src.embedder.base_node_embedder.pinecone_base import AbstractEmbedder
from src.logger.default_logger import logger


class NodeTextEmbedderQdrant(AbstractEmbedder):
    """
    Embeds node texts using OpenAI and stores/retrieves them from Qdrant.
    """

    def __init__(self, model_name=None, api_key=None, **encode_kwargs):
        self.embedding_model = OpenAIEmbeddings(model=model_name, api_key=api_key, **encode_kwargs)
        
       
    def embed_documents(self, texts: List[str]) -> List[Any]:
        try:
            batch_size = 80
            if len(texts) > batch_size:
                all_embeddings = []
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    embeddings = self.embedding_model.embed_documents(batch)
                    all_embeddings.extend(embeddings)
                return all_embeddings
            else:
                return self.embedding_model.embed_documents(texts)
        except Exception as e:
            logger.error(f"An error occurred during document embedding: {e}", exc_info=True)
            return []

    def __call__(self, node_batch) -> Dict[str, List[Dict]]:
        try:
            nodes = node_batch
            logger.debug("Processing batch of nodes: %d", len(nodes))

            texts = [node["payload"]['text'] for node in nodes]
            logger.debug("Extracted text data for embedding. Type: %s", type(texts))

            embeddings = self.embed_documents(texts)
            assert len(nodes) == len(embeddings), "The number of nodes and embeddings must match."

            # Prepare Qdrant points
            points = []
            for node, embedding in zip(nodes, embeddings):
                node_id = node.get("id")
                payload = node.get("payload", {})
                points.append({
                    "id": node_id,
                    "vector": embedding,
                    "payload": payload
                })
        


            return {"embedded_nodes": points}
        except Exception as e:
            logger.error(f"An error occurred while processing nodes: {e}", exc_info=True)
            return {"embedded_nodes": []}
