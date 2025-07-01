import os
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab

load_dotenv()
CELERY_BROKEN_URL = os.environ.get("CELERY_BROKEN_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
SCHEDULER_TIME = int(os.environ.get("SCHEDULER_TIME", 50))
DEFAULT_CELERY_TASK_EXP = os.environ.get("DEFAULT_CELERY_TASK_EXP", 86400)
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", False)

#create Celery instance
celery_app = Celery("import_chat_worker", broker=CELERY_BROKEN_URL, backend=CELERY_RESULT_BACKEND)
celery_app.autodiscover_tasks(['src.celery_worker_hub.import_worker.tasks.file_upload.upload_stream_to_s3', 
                               'src.celery_worker_hub.import_worker.periodic_task.update_failed_ttl',
                               'src.celery_worker_hub.import_worker.tasks.file_upload.zip_process_and_upload_files',
                               'src.celery_worker_hub.import_worker.tasks.extract_transform_openai.extract_and_transform_openai',
                               'src.celery_worker_hub.import_worker.tasks.bulk_update.bulk_update_task',
                               'src.celery_worker_hub.import_worker.tasks.extract_transform_anthropic.extract_and_transform_anthropic'],force=True)
celery_app.conf.task_routes = {"src.celery_worker_hub.import_worker.tasks.file_upload.upload_stream_to_s3": {"queue": "upload_stream_to_s3"},"src.celery_worker_hub.import_worker.tasks.file_upload.zip_process_and_upload_files": {"queue": "upload_zip_file"},
'src.celery_worker_hub.import_worker.tasks.extract_transform_openai.extract_and_transform_openai':{"queue":"extract_and_transform_openai"},
'src.celery_worker_hub.import_worker.tasks.bulk_update.bulk_update_task':{'queue':'bulk_update_task'},
'src.celery_worker_hub.import_worker.tasks.extract_transform_anthropic.extract_and_transform_anthropic':{'queue':'extract_and_transform_anthropic'}}


celery_app.conf.update(
    task_track_started=True,
    task_acks_late = True,
    acks_on_failure_or_timeout = False,
    task_expires=DEFAULT_CELERY_TASK_EXP,
    CELERY_TASK_ALWAYS_EAGER=CELERY_TASK_ALWAYS_EAGER,
    CELERY_TASK_REJECT_ON_WORKER_LOST = True,
    worker_prefetch_multiplier=3,
    worker_max_tasks_per_child=5,
    broker_transport_options={'visibility_timeout': 300}
)

celery_app.conf.beat_schedule = {
    'update-failed-tasks-ttl-every-night': {
        'task': 'src.celery_worker_hub.periodic_task.update_failed_ttl.update_failed_tasks_ttl',
        'schedule': crontab(minute=SCHEDULER_TIME),
    },
}