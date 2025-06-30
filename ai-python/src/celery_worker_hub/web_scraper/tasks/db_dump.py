from fastapi import HTTPException,status
from src.celery_worker_hub.web_scraper.celery_app import celery_app
from src.db.config import db_instance
from bson.objectid import ObjectId
from src.logger.default_logger import logger
from src.celery_worker_hub.web_scraper.utils.update_token import update_tokens,update_child_tokens
from typing import List
from pymongo import UpdateOne

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
)
def dump_to_db(self, summary_data: dict,  parent_prompt_id: str = None,child_prompt_ids:List=None,collection: str = None,) -> dict:
    try:
        if parent_prompt_id:
            # Handle parent document
            query = {"_id": ObjectId(parent_prompt_id)}
            existing_doc = db_instance[collection].find_one(query)

            # Update tokens for parent document
            summary_data = update_tokens(summary_data, existing_doc)

            # Update or insert the parent document
            db_instance[collection].update_one(query, summary_data)

            logger.info("Successfully updated/inserted the parent document with new data.")

        
        if len(child_prompt_ids)>0:
            operations = []
    
            for child_id in child_prompt_ids:
                if child_id!=parent_prompt_id:
            
                    # Call function to update tokens specific to child documents
                    updated_summary_data = update_child_tokens(summary_data)
                
                    query = {"_id": ObjectId(child_id)}
                    update_operation = UpdateOne(query, updated_summary_data, upsert=False)
                    
                    # Append the operation to the list
                    operations.append(update_operation)
                
            if len(operations)>0:
                db_instance[collection].bulk_write(operations)
                

        return {"status": "success", "message": "Documents updated/inserted successfully"}

    except Exception as e:
        logger.error(f"Database operation failed: {e}", extra={"tags": {"method": "ScrapUrlService.dump_to_db"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database operation failed: {e}")
