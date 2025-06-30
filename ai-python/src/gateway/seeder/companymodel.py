from typing import List, Dict, Any
from datetime import datetime
import pytz
from src.db.config import db_instance
from src.logger.default_logger import logger
from pathlib import Path
import json

class CompanyModelSeeder:
    def __init__(self, json_file_path: str = None):
        self.seed_data = self.load_seed_data(json_file_path)
        self.timezone = pytz.timezone("Asia/Kolkata")
        self.company_collection = db_instance.get_collection("company")
        self.model_collection = db_instance.get_collection("model")
        self.company_model_collection = db_instance.get_collection("companymodel")

    def load_seed_data(self, json_file_path: str = None) -> List[Dict[str, Any]]:
        try:
            if not json_file_path:
                json_file_path = Path(__file__).parent / "json" / "company_models_seed.json"
            else:
                json_file_path = Path(json_file_path)

            if not json_file_path.exists() or not json_file_path.is_file():
                logger.warning(f"⚠️ Seed file not found. Skipping seeding process. Path: {json_file_path.resolve()}")
                return []

            # ✅ Only runs if file exists
            with open(json_file_path.resolve(), "r") as file:
                return json.load(file)

        except json.JSONDecodeError as e:
            logger.error(f"⚠️ Invalid JSON format. Skipping data seeding. Error: {e}")
            return []

        except Exception as e:
            logger.error(f"🚨 Unexpected error while loading seed data. Skipping. Error: {e}")
            return []


    def seed(self):
        logger.info("➕🗃️ Starting company model seeding process...")
        current_datetime = datetime.now(self.timezone)
        inserted, skipped = [], []
    
        for model in self.seed_data:
            company = self.company_collection.find_one({"slug": model["company_slug"]})
    
            if not company:
                logger.warning(f"❌ Company not found: {model['company_slug']}")
                skipped.append({"name": model["name"], "reason": "Company not found"})
                continue  # don't raise exception, just skip
            
            existing = self.company_model_collection.find_one({
                "name": model["name"],
                "company.id": company["_id"]
            })
            if existing:
                skipped.append({"name": model["name"], "reason": "Already exists"})
                continue
            
            model_data = self.model_collection.find_one(
                {"code": model["code"]}, {"_id": 1, "title": 1, "code": 1}
            )
            if not model_data:
                logger.error(f"❌ Bot model not found: {model['code']}")
                skipped.append({"name": model["name"], "reason": "Bot model not found"})
                continue
            
            bot_data = {
                "title": model_data["title"],
                "code": model_data["code"],
                "id": model_data["_id"]
            }
    
            company_data = {
                "name": company["companyNm"],
                "slug": company["slug"],
                "id": company["_id"]
            }
    
            record = {
                "name": model["name"],
                "bot": bot_data,
                "company": company_data,
                "config": model["config"],
                "modelType": model["modelType"],
                "isActive": True,
                "extraConfig": model["extraConfig"],
                "__v": 0,
                "createdAt": current_datetime,
                "updatedAt": current_datetime
            }
    
            self.company_model_collection.insert_one(record)
            inserted.append(model["name"])

        if skipped:
            skipped_names = [item["name"] for item in skipped]
            logger.info(f"ℹ️ Skipped models (already exist): {skipped_names}")

        logger.info("✅ Company model seeding completed.")
        logger.info(f"📌 Total Inserted: {len(inserted)}, Skipped: {len(skipped)}")
    
        return {
            "message": "Seeding completed",
            "inserted": inserted,
            "skipped": skipped
        }