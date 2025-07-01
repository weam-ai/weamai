from fastapi import FastAPI, HTTPException, Request, APIRouter, Depends, status
from src.db.redis_config import redis_url
from src.db.config import db_instance
import aioredis
import os
from src.db.redis_config import redis_url
from src.redis_update.llm_models import  RedisLLMModelInitService
from src.round_robin.model_config import ModelConfigService
from src.gateway.jwt_decode import get_user_data
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import pytz
load_dotenv()

router = APIRouter()
class ModelConfigService:
    def __init__(self):
        
        self.db = db_instance
        
        self.company_model = "companymodel"
        self.model = "model"
        self.company = 'company'
        self.setting = 'setting'
    
  
    

    def get_api_keys_and_models(self,functionality=None):
        # Step 1: Get distinct model codes
        list_code = self.db[self.model].distinct("code")        
        # Step 2: Get keys for ROUND_ROBIN
        settings = self.db[self.company_model].find({"code": "ROUND_ROBIN"}, {"_id": 0, f"{functionality}": 1,'company.id':1,'companyKeys':1})
        API_KEYS = {}
        MODELS = {}
        models_list = {}
        for code in list_code:
                models_list[code] = self.db[self.company_model].distinct("name", {"bot.code": code})
        for setting in settings:
            keys = setting.get(functionality, {}) if setting else {}
            company_id = str(setting.get('company').get('id')) if setting.get('companyKeys') else 'default'
            # Step 3: Get company model names for bot.code = OPEN_AI

            # Step 4: Build final structure
            if company_id not in API_KEYS:
                 API_KEYS[company_id] = {}
                 MODELS[company_id] = {}

            for code in list_code:
                API_KEYS[company_id][code] = keys.get(code, [])
                MODELS[company_id][code] = set(models_list.get(code, []))  # maintain models specific to each code
        return API_KEYS, MODELS
    
    def add_roundRobin_field(self,company_id:str):
        company_details = self.db[self.company].find_one({"_id": ObjectId(company_id)}, {"_id": 1,'companyNm':1,'slug':1})
        key_details = self.db[self.setting].find_one({"code": "ROUND_ROBIN"})
        timezone = pytz.timezone("Asia/Kolkata")
        if not company_details:
            raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
        round_robin_document = {
            "_id": ObjectId(),
            "name": "Round Robin",
            "code": "ROUND_ROBIN",
            "createdAt": datetime.now(timezone),
            "updatedAt": datetime.now(timezone),
            "__v": 0,
            "CHAT": {
            "OPEN_AI": key_details['CHAT']['OPEN_AI'],
            "ANTHROPIC": key_details['CHAT']['ANTHROPIC'],
            "GEMINI": key_details['CHAT']['GEMINI'],
            "PERPLEXITY": key_details['CHAT']['PERPLEXITY']
            },
            "company": {
            "name": company_details.get("companyNm"),
            "slug": company_details.get("slug"),
            "id": company_details.get("_id")
            },
            "companyKeys": False
        }
        self.db[self.company_model].insert_one(round_robin_document)



@router.post("/get_best_key/")
async def get_best_key(request: Request,current_user=Depends(get_user_data)):
   
    data = await request.json()
    print("Received data:", data)  # Debugging line to check incoming data
    # Async Redis client    

   
    provider = data.get("provider")
    model = data.get("model")
    functionality = data.get("functionality", "CHAT")  # Default to "CHAT" if not provided




    usage_zset = f"token_usage:{functionality}:{provider}:{model}"
    async with aioredis.from_url(redis_url, decode_responses=True) as redis:
        best_keys = await redis.zrange(usage_zset, 0, 0)
    if not best_keys:
        raise HTTPException(status_code=404, detail="No API keys found for this provider/model")

    return {"best_key": best_keys[0]}



@router.post("/update_usage/")
async def update_usage(request: Request,current_user=Depends(get_user_data)):
    data = await request.json()
    provider = data.get("provider")
    model = data.get("model")
    api_key = data.get("api_key")
    tokens_used = data.get("tokens_used")
    functionality = data.get("functionality", "CHAT")  # Default to "CHAT" if not provided
    usage_zset = f"token_usage:{functionality}:{provider}:{model}"
    async with aioredis.from_url(redis_url, decode_responses=True) as redis:
        await redis.zincrby(usage_zset, tokens_used, api_key)

    return {"message": "Usage updated", "api_key": api_key, "tokens_added": tokens_used}



@router.post("/chat_register_models/")
async def register_redis_models(request: Request,current_user=Depends(get_user_data)):
    model_service = ModelConfigService()
    API_KEYS, MODELS = model_service.get_api_keys_and_models(functionality="CHAT")
    token_service = RedisLLMModelInitService(redis_url, MODELS, API_KEYS,functionality="CHAT")
    await token_service.initialize()