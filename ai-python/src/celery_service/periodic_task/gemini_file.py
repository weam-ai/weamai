# src/celery_service/periodic_task/cleanup.py

from datetime import datetime, timezone
from src.celery_service.celery_worker import celery_app
from src.logger.default_logger import logger
import os
from dotenv import load_dotenv
from src.db.config import get_field_by_name
from google import genai
from src.crypto_hub.utils.crypto_utils import crypto_service
load_dotenv()

@celery_app.task
def delete_old_records():
    """Delete old files from Gemini."""
    try:
        qa_specialist_key = get_field_by_name(collection_name="setting",name="PRO_AGENT",field_name="details")
        gemini_key = qa_specialist_key.get("qa_specialist").get("gemini")
        client = genai.Client(api_key=crypto_service.decrypt(gemini_key))
        deleted_file=[]


        try:
            files = client.files.list()
        except Exception:
            logger.warning("Unable to retrieve files from Gemini API.")
            return


        for f in files:
            try:
                file_age = (datetime.now(timezone.utc) - f.update_time).total_seconds()
                if (f.state.name != "PROCESSING") and file_age > 600:
                    deleted_file.append(f.name)
                    client.files.delete(name=f.name)
            except Exception as file_err:
                logger.error(
                    "Failed to delete file from Gemini.",
                    extra={
                        "tags": {"task_function": "delete_old_records"},
                        "file_name": getattr(f, "name", "<unknown>"),
                        "exception": str(file_err),
                    }
                )

        count_file=len(deleted_file)
        deleted_file=",".join(deleted_file)

        logger.info(f"Total Deleted File {count_file} document(s) {deleted_file} older than 10 minutes.")
        return {"count_file":count_file,"deleted_file":deleted_file}
    except Exception as e:
        logger.error(
            f"Error deleting old records from MongoDB: {e}",
            extra={"tags": {"task_function": "delete_old_records"}}
        )
        return {}
