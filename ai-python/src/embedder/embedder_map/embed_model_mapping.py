
from src.embedder.openai_embedder.pincone_node import NodeTextEmbedderOpenAI
from src.embedder.ray_serve_embedder.pinecone_node import NodeTextEmbedderRayServe
from src.embedder.openai_embedder.qdrant_node import NodeTextEmbedderQdrant
# Dictionary mapping embedding service names to their corresponding text embedder classes.
# This allows for easy selection and instantiation of a specific text embedding service in the application.
# Available services:
# - "pinecone": Uses the Pinecone service for text embedding, handled by NodeTextEmbedderPinecone.
# - "openai": Uses the OpenAI service for text embedding, handled by NodeTextEmbedderOpenAI.
pinenode_text_embedder = {
    "openai": NodeTextEmbedderOpenAI,
    "embrayserve":NodeTextEmbedderRayServe
}
qdrant_text_embedder = {
    "qdrant": NodeTextEmbedderQdrant
}
