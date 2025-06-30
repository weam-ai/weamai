from fastapi import HTTPException
import aioredis
from src.db.redis_config import redis_url
import redis
class APIKeySelectorService:
    def __init__(self):
        self.redis_url = redis_url
    async def get_best_api_key(self, provider: str, model: str,functionality:str) -> str:

        try:
            usage_zset = f"token_usage:{functionality}:{provider}:{model}"
            async with aioredis.from_url(self.redis_url, decode_responses=True) as redis:
                best_keys = await redis.zrange(usage_zset, 0, 0)
            
            self.get_best_api_key_from_redis = best_keys[0]
            

            return best_keys[0]
        except:
            return None
    
    def sync_get_best_api_key(self, provider: str, model: str, functionality: str,company_id:str) -> str:
        try:
            usage_zset = f"token_usage:{functionality}:{company_id}:{provider}:{model}"
            
            # Use redis.Redis (sync version)
            redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
            
            # zrange is synchronous here
            best_keys = redis_client.zrange(usage_zset, 0, 0)
            
            self.get_best_api_key_from_redis = best_keys[0] if best_keys else None
            
            return best_keys[0] if best_keys else None
        except:
            return None
    



class APIKeyUsageService:
    def __init__(self):
        self.redis_url = redis_url
        self.anthropic_weights = {'claude-3-7-sonnet-latest':2.5,'claude-opus-4-20250514':2.5,'claude-sonnet-4-20250514':2.5,'claude-3-5-sonnet-latest':5,'claude-3-5-haiku-latest':5,'claude-3-opus-latest':5}
    async def update_usage(self, provider: str, model: str, api_key: str, tokens_used: int,functionality:str,company_id:str) -> dict:
        usage_zset = f"token_usage:{functionality}:{company_id}:{provider}:{model}"
        async with aioredis.from_url(self.redis_url, decode_responses=True) as redis:
            await redis.zincrby(usage_zset, tokens_used, api_key)
        return {"message": "Usage updated", "api_key": api_key, "tokens_added": tokens_used}

    def update_usage_sync(self, provider: str, model: str, api_key: str, tokens_used: int, functionality: str,company_id:str) -> dict:
        usage_zset = f"token_usage:{functionality}:{company_id}:{provider}:{model}"
        
        # Use redis.Redis (sync version)
        redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        
        # zincrby is synchronous here
        redis_client.zincrby(usage_zset, tokens_used, api_key)
        
        return {"message": "Usage updated", "api_key": api_key, "tokens_added": tokens_used}
    
    async def update_usage_anthropic(self, provider: str, model: str, api_key: str, tokens_used: dict,functionality:str,company_id:str) -> dict:
        usage_zset = f"token_usage:{functionality}:{company_id}:{provider}:{model}"
        if type(tokens_used) is dict:
            if tokens_used['completion']==0:
                tokens_used = 0
            else:    
                tokens_used =tokens_used['promptT']+(tokens_used['completion']*self.anthropic_weights.get(model,2.5))
        else:
            if tokens_used.completion_tokens==0:
                tokens_used = 0
            else:
                tokens_used = tokens_used.prompt_tokens+(tokens_used.completion_tokens*self.anthropic_weights.get(model,2.5))
        async with aioredis.from_url(self.redis_url, decode_responses=True) as redis:
            await redis.zincrby(usage_zset, tokens_used, api_key)
        return {"message": "Usage updated", "api_key": api_key, "tokens_added": tokens_used}

    def update_usage_sync_anthropic(self, provider: str, model: str, api_key: str, tokens_used: dict, functionality: str,company_id:str) -> dict:
        usage_zset = f"token_usage:{functionality}:{company_id}:{provider}:{model}"
        if type(tokens_used) is dict:
            if tokens_used['completion']==0:
                tokens_used = 0
            else:    
                tokens_used =tokens_used['promptT']+(tokens_used['completion']*self.anthropic_weights.get(model,2.5))
        else:
            if tokens_used.completion_tokens==0:
                tokens_used = 0
            else:
                tokens_used = tokens_used.prompt_tokens+(tokens_used.completion_tokens*self.anthropic_weights.get(model,2.5))
        # Use redis.Redis (sync version)
        redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        
        # zincrby is synchronous here
        redis_client.zincrby(usage_zset, tokens_used, api_key)
        
        return {"message": "Usage updated", "api_key": api_key, "tokens_added": tokens_used}
