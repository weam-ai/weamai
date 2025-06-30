import os
import aioredis
import asyncio
from src.celery_service.celery_worker import celery_app
from src.db.redis_config import redis_url
from src.round_robin.model_config import ModelConfigService
REDIS_HOST = os.environ.get("REDIS_URI", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB   = int(os.environ.get("DB_NUMBER", 7))

redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"






@celery_app.task
def model_usage_task():
    async def reset_all_usage():
        model_service = ModelConfigService()
        functionality = "CHAT"
        API_KEYS, MODELS = model_service.get_api_keys_and_models(functionality=functionality)
        async with aioredis.from_url(redis_url, decode_responses=True) as redis:
            for company in API_KEYS:
                for provider, models in MODELS[company].items():
                    for model in models:
                        usage_zset = f"token_usage:{functionality}:{company}:{provider}:{model}"
                        pipe = redis.pipeline()
                        for key in API_KEYS.get(company,'default').get(provider, []):
                            pipe.zadd(usage_zset, {key: 0})
                        await pipe.execute()
        return "Reset complete"
    return asyncio.run(reset_all_usage())