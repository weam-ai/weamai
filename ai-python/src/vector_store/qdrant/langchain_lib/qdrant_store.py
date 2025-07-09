
import os
from langchain_qdrant import QdrantVectorStore
from src.db.qdrant_config import qdrant_client
from qdrant_client import models
from src.vector_store.qdrant.langchain_lib.base import AbstractQdrantVectorStore
from langchain_community.embeddings import OpenAIEmbeddings
from src.crypto_hub.services.openai.embedding_api_key_decryption import EmbeddingAPIKeyDecryptionHandler
from langchain.retrievers import MergerRetriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from typing import List
from pydantic import Field
from langchain.docstore.document import Document
import re
from src.vector_store.qdrant.langchain_lib.config import ExcelVectorStoreConfig
from src.celery_service.openai.excel_agent import run_excel_query
from src.celery_worker_hub.extraction.utils import map_file_url
import os
BUCKET_TYPE_MAP = {
    "LOCALSTACK": "localstack",  # Localstack is used for local development
    "AWS_S3": "s3_url",
    "MINIO": "minio",  # Minio is used for local development
                              # S3 is used for production
}
chunk_pattern = re.compile(r'chunk:(\d+):')

IMAGE_SOURCE_BUCKET = BUCKET_TYPE_MAP.get(os.environ.get("BUCKET_TYPE"))
FILE_SOURCE_BUCKET = BUCKET_TYPE_MAP.get(os.environ.get("BUCKET_TYPE"))

embedding_apikey_decrypt_service=EmbeddingAPIKeyDecryptionHandler()
class QdrantVectorStoreService(AbstractQdrantVectorStore):
    def initialization(
        self,
        company_apikey_id: str = None,
        namespace = "uwp",
        embedder_api_key_id: str = None,
        companypinecone_collection: str = "companypinecone",
        company_model_collection: str = "companymodel",
        text_field: str = "text",
        embedder_class: str = OpenAIEmbeddings,
        **kwargs
    ):
        """
        Initialize the Qdrant vector store.
        :param company_apikey_id: API key for Qdrant.
        :param namespace: Namespace for the index.
        :param embedder_api_key_id: API key for the embedding model.
        :param collection_name: Name of the Qdrant collection.
        :param text_field: Field in the documents to index.
        :param embedder_class: Embedding class to be used.
        """
        

        self.index_name = company_apikey_id
        self.text_field = text_field
        self.namespace = namespace
        embedding_apikey_decrypt_service.initialization(
            api_key_id=embedder_api_key_id,
            collection_name=company_model_collection
        )
        self.embedder = embedder_class(
            model=embedding_apikey_decrypt_service.model_name,
            api_key=embedding_apikey_decrypt_service.decrypt(),
            dimensions=embedding_apikey_decrypt_service.dimensions
        )

        # Initialize qdrant
        self.client = qdrant_client
        self.collection_name =company_apikey_id
        

        # Initialize the vector store
        self.vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedder,
        )


    def index_document(self, document_id, document):
        """
        Index a document in the Qdrant vector store.
        :param document_id: Unique identifier for the document.
        :param document: Document text to be indexed.
        """
        vector = self.embedder.embed(document[self.text_field])
        self.vectorstore.upsert(id=document_id, item=vector)

    def query(self, query_text, top_k=10,tag:str=None):
        """
        Query the vector store and return the top_k closest documents.
        :param query_text: Query text.
        :param top_k: Number of results to return.
        """
        chunk_str= ''
        filter = models.Filter(
                        must=[
                            models.FieldCondition(
                                key="brain_id",
                                match=models.MatchValue(value=self.namespace),
                            ),
                            models.FieldCondition(
                                key="tag",
                                match=models.MatchValue(value=tag),
                            ),
                            # Add more FieldCondition's here as needed
                        ]
                    )
        retriever=self.vectorstore.as_retriever(search_kwargs={'k': top_k, "filter": filter,'with_payload': True})
        description = retriever.get_relevant_documents(query_text)
        for chunk in description:
            chunk_str+=chunk.page_content
        return chunk_str
    
    def multi_doc_query(self, query_text):
        """
        Query the vector store and return the top_k closest documents.
        :param query_text: Query text.
        :param top_k: Number of results to return.
        """
        chunk_str= ''
        description = self.lotr.get_relevant_documents(query_text)
        for chunk in description:
            chunk_str+=chunk.page_content
        return chunk_str

    def get_document(self, document_id):
        """
        Retrieve a document by its identifier from the vector store.
        :param document_id: Unique identifier for the document.
        """
        return self.vectorstore.get(id=document_id)

    def __call__(self):
        """
        Retrieve the Vector Store Object.
        """
        return self.vectorstore

    def get_vector_store(self):
        """
        Retrieve the Vector Store Object.
        """
        return self.vectorstore
    
    def get_lot_retiver(self,top_k=10,tag_list:list=None):
        reteriver_list=[]
        for tag in tag_list:
            filter = models.Filter(
                        must=[
                            models.FieldCondition(
                                key="brain_id",
                                match=models.MatchValue(value=self.namespace),
                            ),
                            models.FieldCondition(
                                key="tag",
                                match=models.MatchValue(value=tag),
                            ),
                            # Add more FieldCondition's here as needed
                        ]
                    )
            retriever=self.vectorstore.as_retriever(search_kwargs={'k': top_k, "filter":filter,'with_payload': True})
            reteriver_list.append(retriever)
        lotr = MergerRetriever(retrievers=reteriver_list)
        return lotr
    
    def get_lot_retiver_namespace(self,top_k=10,tag_list:list=None,namespace_list:list=None, query:str=None, companymodel:str=None, company_id:str=None):
        reteriver_list=[]
        pattern = r"\.(sql|php|js|html|htm|css|py)$"
        excel_pattern = r"\.(xlsx?|csv|json)$"
        for tag,namespace in zip(tag_list,namespace_list):

            filter = models.Filter(
                        must=[
                            models.FieldCondition(
                                key="brain_id",
                                match=models.MatchValue(value=namespace),
                            ),
                            models.FieldCondition(
                                key="tag",
                                match=models.MatchValue(value=tag),
                            )
                            # Add more FieldCondition's here as needed
                        ]
                    )
            temp_vectorstore = QdrantVectorStore(self.client, collection_name=self.collection_name,embedding=self.embedder,content_payload_key="text")
            if re.search(pattern, tag):
                retriever=CodeRetriever(vectorstore=temp_vectorstore.as_retriever(search_kwargs={'k': ExcelVectorStoreConfig.TOP_K, "filter":filter,'with_payload': True}))
            elif re.search(excel_pattern, tag):
                retriever = ExcelRetriever(vectorstore=temp_vectorstore.as_retriever(search_kwargs={'k': ExcelVectorStoreConfig.TOP_K, "filter": filter,'with_payload': True}),file_path=tag,company_id=company_id, companymodel=companymodel)
            else:
                retriever=temp_vectorstore.as_retriever(search_kwargs={'k': top_k, "filter": filter,'with_payload': True})
            reteriver_list.append(retriever)
        lotr = MergerRetriever(retrievers=reteriver_list)
        self.lotr = lotr
        return lotr

class CodeRetriever(BaseRetriever):
    vectorstore: BaseRetriever
    search_type: str = "mmr"
    search_kwargs: dict = Field(default_factory=dict)

    
    def _get_relevant_documents(self, query: str,run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        results = self.vectorstore.get_relevant_documents(query=query)
        def chunk_key(doc):
            match = chunk_pattern.search(doc.page_content)
            return int(match.group(1)) if match else float('inf')

        results.sort(key=chunk_key)

        # Join sorted content
        text_content = "".join(doc.page_content for doc in results)

        return [Document(page_content=text_content)]
    
class ExcelRetriever(BaseRetriever):
    vectorstore: BaseRetriever
    search_type: str = "mmr"
    search_kwargs: dict = Field(default_factory=dict)
    file_path:str
    company_id:str
    companymodel:str
    
    def _get_relevant_documents(self, query: str,run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        self.file_path=map_file_url('/documents/'+ self.file_path, FILE_SOURCE_BUCKET)
        text_content = run_excel_query.delay(file_path=self.file_path, query=query, company_id=self.company_id, companymodel=self.companymodel).get()['response']
        results=[Document(text_content)]
        return results