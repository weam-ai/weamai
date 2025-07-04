from typing import List, Dict, Any
from langchain_community.embeddings import OpenAIEmbeddings  # Adjust the import according to the actual Langchain module
from src.embedder.base_node_embedder.pinecone_base import AbstractEmbedder
from src.logger.default_logger import logger

class NodeTextEmbedderOpenAI(AbstractEmbedder):
    """
    A class for embedding text data from nodes using OpenAI's language model embeddings.

    Attributes:
        embedding_model (OpenAIEmbeddings): An instance of OpenAIEmbeddings used to generate text embeddings.

    Methods:
        __init__(model_name=None, api_key=None, **encode_kwargs):
            Initializes the text embedder with a specific OpenAI model and API key.
        embed_documents(texts: List[str]) -> List[Any]:
            Embeds a list of text documents using the OpenAI model.
        __call__(node_batch) -> Dict[str, List[Dict]]:
            Processes a batch of nodes, embedding the text data contained in each node.
    """

    def __init__(self, model_name=None, api_key=None, **encode_kwargs):
        """
        Initializes the NodeTextEmbedderOpenAI with a specific OpenAI language model and API key.

        Parameters:
            model_name (str, optional): The name of the OpenAI model to use for embedding.
            api_key (str, optional): The API key for accessing OpenAI's API.
            **encode_kwargs: Additional keyword arguments for the encoding method.
        """
        self.embedding_model = OpenAIEmbeddings(model=model_name, openai_api_key=api_key, **encode_kwargs)

    def embed_documents(self, texts: List[str]) -> List[Any]:
        """
        Embeds a list of text documents using the OpenAI embedding model.

        Parameters:
            texts (List[str]): A list of text documents to be embedded.

        Returns:
            List[Any]: A list of embeddings, one for each input text document.
        """
        try:
            batch_size=80
            if len(texts)>batch_size:
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
        """
        Processes a batch of nodes, embedding the text data contained within each node's metadata.

        Parameters:
            node_batch (Dict): A batch of nodes, where each node is expected to contain text data in its metadata.

        Returns:
            Dict[str, List[Dict]]: A dictionary containing the embedded nodes.
        """
        try:
            
            nodes = node_batch
            logger.debug("Processing batch of nodes: %d", len(nodes))

            text = [node["metadata"]['text'] for node in nodes]
            logger.debug("Extracted text data for embedding. Type: %s", type(text))


            embeddings = self.embed_documents(text)

            assert len(nodes) == len(embeddings), "The number of nodes and embeddings must match."

            for node, embedding in zip(nodes, embeddings):
                node['values'] = embedding

            return {"embedded_nodes": nodes}
        except Exception as e:
            logger.error(f"An error occurred while processing nodes: {e}", exc_info=True)

            return {"embedded_nodes": []}
