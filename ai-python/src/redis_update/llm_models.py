import aioredis
import re
from typing import Dict, List



class RedisLLMModelInitService:
    def __init__(self, redis_url: str, models: Dict[str, List[str]], api_keys: Dict[str, List[str]],functionality: str = None):
        self.redis_url = redis_url
        self.models = models
        self.api_keys = api_keys
        self.functionality = functionality

    async def initialize(self):
        async with aioredis.from_url(self.redis_url, decode_responses=True) as redis:
            # Fetch all existing token usage keys
            existing_keys = await redis.keys(f"token_usage:{self.functionality}:*")

            # Remove any keys not matching current 
            for company in self.api_keys:
                for key in existing_keys:
                    match = re.match(rf"token_usage:{re.escape(self.functionality)}:([^:]+):(.+)", key)
                    if not match:
                        continue
                    provider, model = match.groups()
                    if provider not in self.models[company] or model not in self.models[company][provider]:
                        await redis.delete(key)

                # Ensure valid keys are initialized
                for provider, model_list in self.models.get(company,'default').items():
                    for model in model_list:
                        usage_zset = f"token_usage:{self.functionality}:{company}:{provider}:{model}"
                        for key in self.api_keys.get(company,'default').get(provider, []):
                            if await redis.zscore(usage_zset, key) is None:
                                await redis.zadd(usage_zset, {key: 0})
