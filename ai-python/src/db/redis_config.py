import os
import aioredis
import asyncio

REDIS_HOST = os.environ.get("REDIS_URI", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB   = int(os.environ.get("DB_NUMBER", 7))

redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

class RedisClientSingleton:
    _instance = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = await aioredis.from_url(redis_url, decode_responses=True)
        return cls._instance

async def get_redis_client():
    """
    Async function to get a singleton Redis client instance.

    :return: aioredis.Redis object
    """
    return await RedisClientSingleton.get_instance()
