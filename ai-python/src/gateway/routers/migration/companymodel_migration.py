from fastapi import HTTPException, status, Depends, APIRouter
from bson import ObjectId
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.gateway.jwt_decode import get_user_data
from pydantic import BaseModel
from datetime import datetime
import pytz
from typing import List, Optional, Dict, Any

router = APIRouter()

class CompanyModelOpenRouter(BaseModel):
    models: List[str]
    provider: str
    code: str
    api_key: str
    model_type: int = 2
    extra_config: Optional[Dict[str, Any]] = None

@router.post("/migrate-company-openrouter-models", summary="Migrate company openrouter models")
async def migrate_company_models(request:CompanyModelOpenRouter, current_user=Depends(get_user_data)):
    try:
        company_collection = db_instance.get_collection("company")
        company_model_collection = db_instance.get_collection("companymodel")
        model_collection = db_instance.get_collection("model")                
        
        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        models_to_add = request.models
        updated_companies = []
        total_migrated_count = 0

        model_data = model_collection.find_one({"code": request.code}, {"_id": 1, "title": 1, "code": 1, "provider": 1})
        if not model_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model Data not found.")
        
        bot_data = {
            "title": model_data["title"],
            "code": model_data["code"],
            "id": model_data["_id"]
        }

        # Get all companies from the collection
        companies = company_collection.find({})
        for company in companies:
            company_id = company["_id"]
            company_name = company["companyNm"]
            models_inserted = []
            
            for model_name in models_to_add:
                existing_record = company_model_collection.find_one({"name": model_name, "company.id": company_id})

                # If the model does not exist, insert it
                if not existing_record:
                    new_record = {
                        "name": model_name,
                        "bot": bot_data,
                        "provider": model_data["provider"],
                        "company": {
                            "name": company_name,
                            "slug": company["slug"],
                            "id": company_id
                        },
                        "config": {"apikey": request.api_key,"openai_api_base":"https://openrouter.ai/api/v1"},
                        "modelType": request.model_type,
                        "isActive": True,
                        "extraConfig": request.extra_config if request.extra_config else {},
                        "createdAt": current_datetime,
                        "updatedAt": current_datetime
                    }

                    # Insert the new model into the companymodel collection
                    company_model_collection.insert_one(new_record)
                    models_inserted.append(model_name)

            # Check if any models were inserted for this company
            if models_inserted:
                updated_companies.append({
                    "companyName": company_name,
                    "modelsInserted": models_inserted,
                    "totalModelsInserted": len(models_inserted)
                })
                total_migrated_count += 1
                logger.info(f"Inserted {len(models_inserted)} models for company {company_name}.")
            else:
                logger.info(f"No models inserted for company {company_name}.")

        # Check if any companies were updated
        if total_migrated_count > 0:
            logger.info(f"Total companies migrated: {total_migrated_count}.")
        else:
            logger.warning("No companies were migrated.")

        return {
            "message": "Migration Companymodel completed successfully.",
            "totalMigratedCount": total_migrated_count,
            "updatedCompanies": updated_companies
        }

    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Migration process encountered an error.")

class SingleCompanyModelOpenRouter(BaseModel):
    company_id: str
    models: List[str]
    provider: str
    code: str
    api_key: str
    model_type: int = 2
    extra_config: Optional[Dict[str, Any]] = None

@router.post("/migrate-company-byid-openrouter-models", summary="Migrate company openrouter models by id")
async def migrate_company_byid_models(request:SingleCompanyModelOpenRouter, current_user=Depends(get_user_data)):
    try:
        company_collection = db_instance.get_collection("company")
        company_model_collection = db_instance.get_collection("companymodel")
        model_collection = db_instance.get_collection("model")                
        
        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        models_to_add = request.models
        updated_companies = []
        total_migrated_count = 0

        model_data = model_collection.find_one({"code": request.code}, {"_id": 1, "title": 1, "code": 1, "provider": 1})
        if not model_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model Data not found.")
        
        bot_data = {
            "title": model_data["title"],
            "code": model_data["code"],
            "id": model_data["_id"]
        }

        company_id = ObjectId(request.company_id)
        # Get specific company from the collection
        company = company_collection.find_one({"_id": company_id})
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
        
        company_name = company["companyNm"]
        models_inserted = []
        
        for model_name in models_to_add:
            existing_record = company_model_collection.find_one({"name": model_name, "company.id": company_id})

            # If the model does not exist, insert it
            if not existing_record:
                new_record = {
                    "name": model_name,
                    "bot": bot_data,
                    "provider": model_data["provider"],
                    "company": {
                        "name": company_name,
                        "slug": company["slug"],
                        "id": company_id
                    },
                    "config": {"apikey": request.api_key,"openai_api_base":"https://openrouter.ai/api/v1"},
                    "modelType": request.model_type,
                    "isActive": True,
                    "extraConfig": request.extra_config if request.extra_config else {},
                    "createdAt": current_datetime,
                    "updatedAt": current_datetime
                }

                # Insert the new model into the companymodel collection
                company_model_collection.insert_one(new_record)
                models_inserted.append(model_name)

        # Check if any models were inserted for this company
        if models_inserted:
            updated_companies.append({
                "companyName": company_name,
                "modelsInserted": models_inserted,
                "totalModelsInserted": len(models_inserted)
            })
            total_migrated_count += 1
            logger.info(f"Inserted {len(models_inserted)} models for company {company_name}.")
        else:
            logger.info(f"No models inserted for company {company_name}.")

        return {
            "message": "Migration Companymodel completed successfully.",
            "totalMigratedCount": total_migrated_count,
            "updatedCompanies": updated_companies
        }

    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Migration process encountered an error.")

class SingleCompanyModel(BaseModel):
    company_id: str
    models: List[str]
    code: str
    api_key: str
    model_type: int = 2
    extra_config: Optional[Dict[str, Any]] = None

@router.post("/migrate-company-byid-models", summary="Migrate company models by id")
async def migrate_company_byid_models(request:SingleCompanyModel, current_user=Depends(get_user_data)):
    try:
        company_collection = db_instance.get_collection("company")
        company_model_collection = db_instance.get_collection("companymodel")
        model_collection = db_instance.get_collection("model")                
        
        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        models_to_add = request.models
        updated_companies = []
        total_migrated_count = 0

        model_data = model_collection.find_one({"code": request.code}, {"_id": 1, "title": 1, "code": 1})
        if not model_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model Data not found.")
        
        bot_data = {
            "title": model_data["title"],
            "code": model_data["code"],
            "id": model_data["_id"]
        }

        company_id = ObjectId(request.company_id)
        # Get specific company from the collection
        company = company_collection.find_one({"_id": company_id})
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
        
        company_name = company["companyNm"]
        models_inserted = []
        
        for model_name in models_to_add:
            existing_record = company_model_collection.find_one({"name": model_name, "company.id": company_id})

            # If the model does not exist, insert it
            if not existing_record:
                new_record = {
                    "name": model_name,
                    "bot": bot_data,
                    "company": {
                        "name": company_name,
                        "slug": company["slug"],
                        "id": company_id
                    },
                    "config": {"apikey": request.api_key},
                    "modelType": request.model_type,
                    "isActive": True,
                    "extraConfig": request.extra_config if request.extra_config else {},
                    "createdAt": current_datetime,
                    "updatedAt": current_datetime
                }

                # Insert the new model into the companymodel collection
                company_model_collection.insert_one(new_record)
                models_inserted.append(model_name)

        # Check if any models were inserted for this company
        if models_inserted:
            updated_companies.append({
                "companyName": company_name,
                "modelsInserted": models_inserted,
                "totalModelsInserted": len(models_inserted)
            })
            total_migrated_count += 1
            logger.info(f"Inserted {len(models_inserted)} models for company {company_name}.")
        else:
            logger.info(f"No models inserted for company {company_name}.")

        return {
            "message": "Migration Companymodel completed successfully.",
            "totalMigratedCount": total_migrated_count,
            "updatedCompanies": updated_companies
        }

    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Migration process encountered an error.")
    
class CompanyModel(BaseModel):
    models: List[str]
    code: str
    api_key: str
    model_type: int = 2
    extra_config: Optional[Dict[str, Any]] = None

@router.post("/migrate-company-models", summary="Migrate company models")
async def migrate_company_models(request:CompanyModel, current_user=Depends(get_user_data)):
    try:
        company_collection = db_instance.get_collection("company")
        company_model_collection = db_instance.get_collection("companymodel")
        model_collection = db_instance.get_collection("model")                
        
        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        models_to_add = request.models
        updated_companies = []
        total_migrated_count = 0

        model_data = model_collection.find_one({"code": request.code}, {"_id": 1, "title": 1, "code": 1})
        if not model_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model Data not found.")
        
        bot_data = {
            "title": model_data["title"],
            "code": model_data["code"],
            "id": model_data["_id"]
        }

        # Get all companies from the collection
        companies = company_collection.find({})
        for company in companies:
            company_id = company["_id"]
            company_name = company["companyNm"]
            models_inserted = []
            
            for model_name in models_to_add:
                existing_record = company_model_collection.find_one({"name": model_name, "company.id": company_id})

                # If the model does not exist, insert it
                if not existing_record:
                    new_record = {
                        "name": model_name,
                        "bot": bot_data,
                        "company": {
                            "name": company_name,
                            "slug": company["slug"],
                            "id": company_id
                        },
                        "config": {"apikey": request.api_key},
                        "modelType": request.model_type,
                        "isActive": True,
                        "extraConfig": request.extra_config if request.extra_config else {},
                        "createdAt": current_datetime,
                        "updatedAt": current_datetime
                    }

                    # Insert the new model into the companymodel collection
                    company_model_collection.insert_one(new_record)
                    models_inserted.append(model_name)

            # Check if any models were inserted for this company
            if models_inserted:
                updated_companies.append({
                    "companyName": company_name,
                    "modelsInserted": models_inserted,
                    "totalModelsInserted": len(models_inserted)
                })
                total_migrated_count += 1
                logger.info(f"Inserted {len(models_inserted)} models for company {company_name}.")
            else:
                logger.info(f"No models inserted for company {company_name}.")

        # Check if any companies were updated
        if total_migrated_count > 0:
            logger.info(f"Total companies migrated: {total_migrated_count}.")
        else:
            logger.warning("No companies were migrated.")

        return {
            "message": "Migration Companymodel completed successfully.",
            "totalMigratedCount": total_migrated_count,
            "updatedCompanies": updated_companies
        }

    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Migration process encountered an error.")
    
@router.post("/migrate-round-robin-model", summary="Migrate Round Robin model to all companies")
async def migrate_round_robin_model(current_user=Depends(get_user_data)):
    try:
        company_collection = db_instance.get_collection("company")
        company_model_collection = db_instance.get_collection("companymodel")
        setting=db_instance.get_collection("setting")          
        key_details = setting.find_one({"code": "ROUND_ROBIN"})
        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        inserted_count = 0
        updated_companies = []

        companies = company_collection.find({})

        for company in companies:
            company_id = company["_id"]
            company_name = company.get("companyNm")
            company_slug = company.get("slug")

            # Check if Round Robin model already exists for this company
            exists = company_model_collection.find_one({
                "code": "ROUND_ROBIN",
                "company.id": company_id
            })

            if not exists:
                round_robin_record = {
                    "name": "Round Robin",
                    "code": "ROUND_ROBIN",
                    "createdAt": current_datetime,
                    "updatedAt": current_datetime,
                    "__v": 0,
                    "CHAT": {
                    "OPEN_AI": key_details['CHAT']['OPEN_AI'],
                    "ANTHROPIC": key_details['CHAT']['ANTHROPIC'],
                    "GEMINI": key_details['CHAT']['GEMINI'],
                    "PERPLEXITY": key_details['CHAT']['PERPLEXITY']
                    },
                    "company": {
                        "name": company_name,
                        "slug": company_slug,
                        "id": company_id
                    },
                    "companyKeys": False
                }

                company_model_collection.insert_one(round_robin_record)
                inserted_count += 1
                updated_companies.append(company_name)
                logger.info(f"✅ Inserted Round Robin model for company: {company_name}")
            else:
                logger.info(f"⏭️ Model already exists for company: {company_name}")

        return {
            "message": "Round Robin model migration completed.",
            "totalMigrated": inserted_count,
            "companiesUpdated": updated_companies
        }

    except Exception as e:
        logger.exception("❌ Round Robin migration failed.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Migration error: {str(e)}"
        )
    
class CompanyDetails(BaseModel):
    company_id: str

@router.post("/update-roundRobin-field", summary="Update Round Robin model to specific company")
def update_roundRobin_field(request:CompanyDetails,current_user=Depends(get_user_data)):
        company_collection = db_instance.get_collection('company')
        setting_collection = db_instance.get_collection('setting')
        companyModel_collection = db_instance.get_collection('companymodel')
        company_details = company_collection.find_one({"_id": ObjectId(request.company_id)}, {"_id": 1, 'companyNm': 1, 'slug': 1})
        key_details = setting_collection.find_one({"code": "ROUND_ROBIN"})
        timezone = pytz.timezone("Asia/Kolkata")
        if not company_details:
            raise HTTPException(status_code=404, detail=f"Company with ID {request.company_id} not found")
        
        update_fields = {
            "updatedAt": datetime.now(timezone),
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
        
        result = companyModel_collection.update_one(
            {"code": "ROUND_ROBIN", "company.id": company_details.get("_id")},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"Round Robin entry for company ID {request.company_id} not found")
        
        return {"message": "Round Robin entry updated successfully"}

@router.post("/update-roundRobin-field-allCompanies", summary="Update Round Robin model to all companies")
def update_roundRobin_field_for_all_companies(current_user=Depends(get_user_data)):    
        company_collection = db_instance.get_collection('company')
        setting_collection = db_instance.get_collection('setting')
        companyModel_collection = db_instance.get_collection('companymodel')
        companies = company_collection.find({}, {"_id": 1, 'companyNm': 1, 'slug': 1})
        key_details = setting_collection.find_one({"code": "ROUND_ROBIN"})
        timezone = pytz.timezone("Asia/Kolkata")
        
        if not key_details:
            raise HTTPException(status_code=404, detail="ROUND_ROBIN settings not found")
        
        for company_details in companies:
            update_fields = {
                "updatedAt": datetime.now(timezone),
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
            
            result = companyModel_collection.update_one(
                {"code": "ROUND_ROBIN", "company.id": company_details.get("_id")},
                {"$set": update_fields}
            )
            
            if result.matched_count == 0:
                print(f"Round Robin entry for company ID {company_details.get('_id')} not found")
        
        return {"message": "Round Robin entries updated for all companies"}