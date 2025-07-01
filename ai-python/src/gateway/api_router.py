from src.gateway.routers import doc_chats
from src.gateway.routers import simple_chat
from src.gateway.routers import title_chats
from src.gateway.routers import image_generate
from src.gateway.routers import custom_gpt_doc
from src.gateway.routers import scrape
from src.gateway.routers import validate_endpoint
from src.gateway.routers import browser_chat
from src.gateway.routers import enhance_query
from src.gateway.routers import pro_agent
from src.gateway.routers import video_analysis
from src.gateway.routers import general_multi_vectors
from src.gateway.routers import qdrant
from src.gateway.routers import redis_model
from src.gateway.routers import general_multi_vectors
from fastapi import APIRouter, Depends
from src.gateway.routers import ray, tasks, vectors, tool_chat,canvas_chat,summaries_migration,multi_vectors,migration,import_chat, import_chat_json,seo_apis,sales_call_analyzer,upload_file,playwrite
from dotenv import load_dotenv
load_dotenv()
import os
from src.gateway.utils import verify_security_code, verify_basic_auth

current_environment = os.environ.get("WEAM_ENVIRONMENT", "dev")

api_router = APIRouter()


api_router.include_router(custom_gpt_doc.router,prefix="/pyapi/api/chat",tags=['CustomGPT'])
api_router.include_router(title_chats.router, prefix='/pyapi/api/title', tags=['Title'])
api_router.include_router(simple_chat.router, prefix='/pyapi/api/chat', tags=['Chat'])
api_router.include_router(doc_chats.router, prefix='/pyapi/api/chat', tags=['Chat'])
api_router.include_router(ray.router, prefix='/pyapi/api/ray', tags=['Ray'])
api_router.include_router(tasks.router, prefix='/pyapi/api/task', tags=['Task'])
api_router.include_router(vectors.router, prefix='/pyapi/api/vector', tags=['Vector Store'])
api_router.include_router(multi_vectors.router,prefix='/pyapi/api/vector',tags=['MultiVector Store'])
api_router.include_router(image_generate.router,prefix='/pyapi/api/image',tags=['DALL-E'])
api_router.include_router(scrape.router,prefix='/pyapi/api/scrape',tags=['Scrape'])
api_router.include_router(tool_chat.router,prefix='/pyapi/api/tool',tags=['Tool Chat'])
api_router.include_router(summaries_migration.router,prefix='/pyapi/api/migrate',tags=['Migrate Summries'])
api_router.include_router(canvas_chat.router,prefix='/pyapi/api/canvas',tags=['Canvas Chat'])
api_router.include_router(validate_endpoint.router,prefix='/pyapi/api/validateEndpoint',tags=['Endpoint Validation'])
api_router.include_router(browser_chat.router,prefix='/pyapi/api/browser',tags=['Browser Chat'])
api_router.include_router(migration.migration_router,prefix='/pyapi/api/migration',tags=['Collection Migration'],dependencies=[Depends(verify_basic_auth)])
api_router.include_router(import_chat.router,prefix="/pyapi/api/importchat",tags=["Import Chat"])
api_router.include_router(import_chat_json.router,prefix="/pyapi/api/importchatjson",tags=["Import Chat Json"])
api_router.include_router(enhance_query.router,prefix="/pyapi/api/query",tags=["Enhance Query"])
api_router.include_router(pro_agent.router,prefix="/pyapi/api/agent",tags=["Pro Agent"])
api_router.include_router(seo_apis.router,prefix="/pyapi/api/agent",tags=["Pro Agent"])
api_router.include_router(upload_file.router,prefix="/pyapi/api/upload",tags=["Upload Files"])
api_router.include_router(video_analysis.router,prefix="/pyapi/api/agent",tags=["Upload Files"])
api_router.include_router(playwrite.router,prefix="/pyapi/api/playwrite",tags=["playwrite Content"])
api_router.include_router(redis_model.router,prefix="/pyapi/api/redis_models",tags=["Redis Model"])
api_router.include_router(qdrant.router,prefix="/pyapi/api/qdrant",tags=["Qdrant"])
api_router.include_router(sales_call_analyzer.router,prefix="/pyapi/api/agent",tags=["Pro Agent"])
api_router.include_router(general_multi_vectors.router,prefix="/pyapi/api/vector",tags=["General Multi Vector Store"])



