from fastapi import HTTPException, status, Depends, APIRouter
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.gateway.jwt_decode import get_user_data
from datetime import datetime
import pytz
from pydantic import BaseModel
from bson import ObjectId

router = APIRouter()

class QueryLimitRequest(BaseModel):
    query_key: str
    limit: int

@router.post("/migrate-company-querylimit", summary="Migrate company query limit")
async def migrate_company(request: QueryLimitRequest, current_user=Depends(get_user_data)):
    try:
        company_collection = db_instance.get_collection("company")
        subscription_collection = db_instance.get_collection("subscription")

        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        updated_companies = []
        total_migrated_count = 0
        companies = company_collection.find({})

        for company in companies:
            # Check if company has an ACTIVE subscription
            subscription = subscription_collection.find_one({
                "company.id": company["_id"]
            })

            if subscription:
                logger.info(f"Skipping company '{company['companyNm']}' due to ACTIVE and CANCLE subscription.")
                continue  # Skip this company if subscription is ACTIVE

            query_limit = company.get("queryLimit", {})
            if request.query_key not in query_limit:
                query_limit[request.query_key] = request.limit
                company_collection.update_one(
                    {"_id": company["_id"]},
                    {"$set": {"queryLimit": query_limit, "updatedAt": current_datetime}}
                )
                updated_companies.append(company["companyNm"])
                total_migrated_count += 1

        if total_migrated_count > 0:
            logger.info(f"Total companies migrated: {total_migrated_count}.")
        else:
            logger.warning("No companies were migrated.")

        return {
            "message": "Migration for company querylimit completed successfully.",
            "totalMigratedCount": total_migrated_count,
            "updatedCompanies": updated_companies
        }

    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Migration process encountered an error.")

class SingleCompanyQueryLimit(BaseModel):
    company_id: str
    query_key: str
    limit: int

@router.post("/migrate-single-company-querylimit", summary="Migrate query limit for a single company")
async def migrate_single_company(request: SingleCompanyQueryLimit, current_user=Depends(get_user_data)):
    try:
        company_collection = db_instance.get_collection("company")
        subscription_collection = db_instance.get_collection("subscription")

        timezone = pytz.timezone("Asia/Kolkata")
        current_datetime = datetime.now(timezone)

        company = company_collection.find_one({"_id": ObjectId(request.company_id)})

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Check if company has an ACTIVE subscription
        subscription = subscription_collection.find_one({
            "company.id": company["_id"],
        })

        if subscription:
            logger.info(f"Skipping company '{company['companyNm']}' due to ACTIVE and CANCLE subscription.")
            return {"message": f"Skipping company '{company['companyNm']}' due to ACTIVE and CANCLE subscription."}

        query_limit = company.get("queryLimit", {})
        if request.query_key not in query_limit:
            query_limit[request.query_key] = request.limit
            company_collection.update_one(
                {"_id": company["_id"]},
                {"$set": {"queryLimit": query_limit, "updatedAt": current_datetime}}
            )
            logger.info(f"Company '{company['companyNm']}' migrated successfully.")
            return {
                "message": "Migration for the company query limit completed successfully.",
                "company": company["companyNm"]
            }
        else:
            return {"message": f"Query key '{request.query_key}' already exists for company '{company['companyNm']}'."}

    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Migration process encountered an error."
        )