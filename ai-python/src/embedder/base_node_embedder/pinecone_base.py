from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Abstract base class for an embedding service
class AbstractEmbedder(ABC):
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[Any]:
        """
        Embeds a list of text documents.        
        
        :param texts: A list of strings to be embedded.
        :return: A list of embeddings.
        """
        pass

    @abstractmethod
    def __call__(self, items: List[Dict[str, Any]], text_key: str, embedding_key: str) -> List[Dict[str, Any]]:
        """
        Process a batch of items, embed their textual content, and add the embedding back to the items.
        
        :param items: A list of dictionaries, each containing at least the text to be embedded.
        :param text_key: The key in the dictionaries where the text is stored.
        :param embedding_key: The key under which the embedding should be stored in the dictionaries.
        :return: The list of dictionaries, now each including its embedding.
        """
        pass

