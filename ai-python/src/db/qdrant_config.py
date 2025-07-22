import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()
local_qdrant_url = os.environ.get("LOCAL_QDRANT_URL", None)
qdrant_url=os.environ.get("QDRANT_URL", None)
qdrant_api_key=os.environ.get("QDRANT_API_KEY", None)



if qdrant_url and qdrant_api_key:
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
else:
    qdrant_client = QdrantClient(url=local_qdrant_url)