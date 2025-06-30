import json
from typing import Dict
from langchain.embeddings import HuggingFaceEmbeddings
import torch
import time
import ray
from ray import serve
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from starlette.requests import Request

app = FastAPI()

# Asynchronous function to resolve incoming JSON requests
async def json_resolver(request: Request) -> dict:
    """
    Resolve incoming JSON requests asynchronously.

    Args:
        request: The incoming HTTP request containing JSON data.

    Returns:
        A dictionary representing the parsed JSON data.
    """
    return await request.json()


# Step 1: Wrap the pretrained sentiment analysis model in a Serve deployment.
@serve.deployment
@serve.ingress(app)
class ModelDeployment:
    def __init__(self):
        """
        Initialize the ModelDeployment class.

        This constructor initializes the class and loads the pretrained sentiment analysis model.
        """
        self._model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        

    @app.post("/")
    async def embedding(self, request: Request) -> Dict:
        """
        Embed texts using sentence transformers.

        Args:
            data: The input data containing a list of texts to embed.

        Returns:
            A dictionary containing embeddings of input texts, each represented as a list of floats.
        """
        data = await request.json()
        input_texts = data['input']
        embeddings = [torch.from_numpy(self._model.encode(text, convert_to_numpy=True)).tolist() for text in input_texts]
        response = {'data': embeddings}
        return response


ray.init()
serve.start()

serve.run(ModelDeployment.bind(),route_prefix="/model")


