from starlette.requests import Request
from ray import serve
from langchain_community.embeddings import HuggingFaceEmbeddings
import torch
import gc
from fastapi import APIRouter
from logger.default_logger import logger
serve_route=APIRouter()
@serve.deployment(ray_actor_options={"num_gpus": 0.2, "num_cpus": 0.5}, autoscaling_config={"min_replicas": 1, "max_replicas": 2})
@serve.ingress(serve_route)
class ModelDeploymentHeadEMbedHF:
    def __init__(self):
        self.model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"}
        self.encode_kwargs = {"batch_size": 400}
        self.models_cache = {}

    def get_or_load_model(self, model_name: str):
        if model_name not in self.models_cache:
            self.models_cache[model_name] = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=self.model_kwargs, encode_kwargs=self.encode_kwargs)
            logger.info(f"Loaded model: {model_name}")

        return self.models_cache[model_name]
    
    @serve_route.post("/")
    async def embedding(self, request: Request):
        data = await request.json()
        input_texts = data.get('input')
        model_name = data.get('model_name', 'sentence-transformers/all-mpnet-base-v2')
        if not input_texts:
            return {"error": "No input texts provided."}
        embedding_model = self.get_or_load_model(model_name)
        embeddings = embedding_model.embed_documents(input_texts)
        gc.collect()
        torch.cuda.empty_cache()
        return {'data': embeddings}
