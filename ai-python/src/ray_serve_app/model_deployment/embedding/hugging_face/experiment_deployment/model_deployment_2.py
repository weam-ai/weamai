from fastapi import FastAPI
from starlette.requests import Request
from ray import serve
from langchain_community.embeddings import HuggingFaceEmbeddings
import ray
import time
from typing import List
from pydantic import BaseModel
from ray.serve.config import AutoscalingConfig
app = FastAPI()
from logger.default_logger import logger


@serve.deployment(ray_actor_options={"num_gpus": 0.02, "num_cpus": 0.5},autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 2
    }
)
@serve.ingress(app)
class ModelDeployment:
    def __init__(self):
        """
        Initializes the default settings for the model.
        """
        import torch
        self.model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"}
        self.encode_kwargs = {"batch_size": 400}
        self.models_cache = {}  # Cache to store models

    def get_or_load_model(self, model_name: str):
        """
        Retrieves a model from the cache or loads it if not present.

        Args:
            model_name: Name of the model to retrieve or load.

        Returns:
            An instance of HuggingFaceEmbeddings.
        """
        if model_name not in self.models_cache:
            self.models_cache[model_name] = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=self.model_kwargs,
                encode_kwargs=self.encode_kwargs
            )
            logger.info(f"Loaded model: {model_name}")
        return self.models_cache[model_name]

    @app.post("/")
    async def embedding(self, request: Request):
        """
        Embed texts using a user-specified sentence transformer model and return embeddings.

        Args:
            request: The incoming HTTP request containing the texts and model name.

        Returns:
            A dictionary containing the embeddings of the input texts.
        """
        data = await request.json()
        input_texts = data.get('input')
        model_name = data.get('model_name', 'sentence-transformers/all-mpnet-base-v2')  # Default model

        if not input_texts:
            return {"error": "No input texts provided."}

        # Retrieve or load the model from the cache
        embedding_model = self.get_or_load_model(model_name)

        embeddings = embedding_model.embed_documents(input_texts)
        return {'data': embeddings}

# Initialize Ray and Serve
ray.init("ray_head:6385")
serve.start(http_options={"host": "0.0.0.0", "port": 8073})
serve.run(ModelDeployment.bind(), route_prefix="/model")

while True:
    time.sleep(0.00001)
