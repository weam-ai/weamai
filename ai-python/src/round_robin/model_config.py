from fastapi import FastAPI, HTTPException, Request, APIRouter, Depends, status
from src.db.config import db_instance

class ModelConfigService:
    def __init__(self):
        
        self.db = db_instance
        
        self.company_model = "companymodel"
        self.model = "model"
    
  
    

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