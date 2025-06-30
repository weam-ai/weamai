from abc import ABC, abstractmethod

class AbstractQdrantVectorStore(ABC):
    @abstractmethod
    def initialization(self):
        pass

    @abstractmethod
    def index_document(self, document_id, document):
        """
        Abstract method to index a document in the Qdrant vector store.
        :param document_id: Unique identifier for the document.
        :param document: Document text to be indexed.
        """
        pass

    @abstractmethod
    def query(self, query_text, top_k=10):
        """
        Abstract method to query the vector store and return the top_k closest documents.
        :param query_text: Query text.
        :param top_k: Number of results to return.
        """
        pass