from typing import List, Dict, Any
import requests
import json
from src.embedder.base_node_embedder.pinecone_base import AbstractEmbedder
from src.logger.default_logger import logger
from src.embedder.config import RayConfig

class NodeTextEmbedderRayServe(AbstractEmbedder):
    """
    A class for embedding text data from nodes using an external Ray Serve service.

    Attributes:
        api_url (str): URL of the Ray Serve API to send text data for embedding.
        headers (Dict[str, str]): HTTP headers for API requests.
        model_kwargs (Dict[str, Any]): Additional keyword arguments for the model configuration.
        encode_kwargs (Dict[str, Any]): Additional keyword arguments for the encoding process.

    Methods:
        __init__(api_url: str, model_kwargs: Dict[str, Any], encode_kwargs: Dict[str, Any]):
            Initializes the text embedder with specific Ray Serve API URL, model configuration, and encoding parameters.
        embed_documents(texts: List[str]) -> List[Any]:
            Embeds a list of text documents using the Ray Serve API.
        __call__(node_batch: Dict) -> Dict[str, List[Dict]]:
            Processes a batch of nodes, embedding the text data contained in each node.
    """

    def __init__(self, api_url: str, model_name:str,model_kwargs: Dict[str, Any]=None, encode_kwargs: Dict[str, Any]=None,dimensions:int=None):
        """
        Initializes the NodeTextEmbedderRayServe with a specific Ray Serve API URL, model configuration, and encoding parameters.

        Parameters:
            api_url (str): The URL of the Ray Serve API for embedding texts.
            model_kwargs (Dict[str, Any]): Additional keyword arguments for the model configuration.
            encode_kwargs (Dict[str, Any]): Additional keyword arguments for the encoding process.
        """
        self.api_url = api_url
        self.headers = {'Content-Type': 'application/json'}
        self.model_kwargs = model_kwargs
        self.encode_kwargs = encode_kwargs

    def embed_documents(self, texts: List[str]) -> List[Any]:
        """
        Embeds a list of text documents using an external Ray Serve API.

        Parameters:
            texts (List[str]): A list of text documents to be embedded.

        Returns:
            List[Any]: A list of embeddings, one for each input text document.
        """
        data = {"input": texts, "model_kwargs": self.model_kwargs, "encode_kwargs": self.encode_kwargs}
        try:
            response = requests.post(self.api_url, json=data, headers=self.headers,timeout=RayConfig.TIMEOUT)
            response.raise_for_status()
            return json.loads(response.text).get("data", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred during document embedding: {e}", exc_info=True)
            return []

    def __call__(self, node_batch: Dict) -> Dict[str, List[Dict]]:
        """
        Processes a batch of nodes, embedding the text data contained within each node's metadata.

        Parameters:
            node_batch (Dict): A batch of nodes, where each node is expected to contain text data in its metadata.

        Returns:
            Dict[str, List[Dict]]: A dictionary containing the embedded nodes.
        """
        try:
            text = [node["metadata"]['text'] for node in node_batch]
            logger.debug("Extracted text data for embedding. Type: %s", type(text))

            embeddings = self.embed_documents(text)
            logger.debug("Embedded sample: %s", embeddings[0] if embeddings else None)

            assert len(node_batch) == len(embeddings), "The number of nodes and embeddings must match."

            for node, embedding in zip(node_batch, embeddings):
                node['values'] = embedding

            return {"embedded_nodes": node_batch}
        except Exception as e:
            logger.error(f"An error occurred while processing nodes: {e}", exc_info=True)
            return {"embedded_nodes": []}
