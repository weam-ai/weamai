from fastapi import FastAPI
from model_deployment.embedding.hugging_face.model_deployment_v4 import ModelDeploymentHeadEMbedHF,serve_route
import ray
from ray import serve
import time
import os
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()
app.include_router(serve_route)
all_env_vars = dict(os.environ)

# Setup the runtime environment with the environment variables
ray_host = str(os.environ.get('RAY_ADDRESS_HOST'))
ray_port = os.environ.get('RAY_HEAD_NODE_PORT')
ray_address = f"{ray_host}:{ray_port}"


ray.init(ray_address,_redis_password=os.environ.get("RAY_REDIS_PASSWORD"))
serve.start(http_options={"host": os.environ.get("RAY_SERVE_HOST") ,"port": int(os.environ.get("RAY_SERVE_PORT"))},detached=True)
serve.run(ModelDeploymentHeadEMbedHF.bind(), route_prefix="/model")
while True:
    time.sleep(0.1)
