from src.celery_worker_hub.extraction.celery_app import celery_app
from src.content_extraction.mapping.file_mapping import get_extractor,is_url_type
from src.celery_service.mongodb.task_status import log_task_status
from fastapi import HTTPException
from src.logger.default_logger import logger
from src.celery_worker_hub.extraction.utils import map_file_url

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 0},
    queue="extraction"
)
def extract_text_task(
    self,
    file_url: str = None,
    file_type: str = None,
    source: str = None,
    page_wise = None,
    tag: str = None,
    **kwargs
):
    try:
        if not source or not file_url:
            raise ValueError("Both source and file_url must be provided.")
        
        file_url = map_file_url(file_url, source)
        log_task_status.apply_async(
            kwargs={
                '_id': kwargs.get("id"),
                'status': 'STARTED',
                'task_progress': 'EXTRACTION',
                'collection': 'file'
            }
        )

        extractor_class = get_extractor(file_type, source)
        extractor = extractor_class(source=file_url, is_url=is_url_type(source))
        extracted_text = extractor.extract_text(eval(page_wise))
        logger.info(
            "Successfully executed text extraction task",
            extra={"tags": {"task_function": "extract_text_task"}}
        )
    except HTTPException as e:
        logger.error(
            f"Error executing text extraction task: {e}",
            extra={"tags": {"task_function": "extract_text_task"}}
        )
        raise HTTPException(status_code=400, detail=str(e))
    return extracted_text
