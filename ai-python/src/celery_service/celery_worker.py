import os
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab

load_dotenv()
CELERY_BROKEN_URL = os.environ.get("CELERY_BROKEN_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
SCHEDULER_TIME = int(os.environ.get("SCHEDULER_TIME", 5))
DEFAULT_CELERY_TASK_EXP = os.environ.get("DEFAULT_CELERY_TASK_EXP", 86400)
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", False)
GOOGLE_SCHEDULER_TIME = int(os.environ.get("GOOGLE_SCHEDULER_TIME", 10))
MODEL_USAGE_RESET_TIME = int(os.environ.get("MODEL_USAGE_RESET_TIME", 1))

#create Celery instance
celery_app = Celery("worker", broker=CELERY_BROKEN_URL, backend=CELERY_RESULT_BACKEND)


celery_app.autodiscover_tasks([
    "src.celery_service.openai.embed_task",
    "src.celery_service.periodic_task.update_failed_ttl",
    'src.celery_service.periodic_task.reset_usage',
    "src.celery_service.periodic_task.gemini_file",
    "src.celery_service.testing_task",
    "src.celery_service.mongodb.task_status",
    "src.celery_service.ray_serve.embed_task",
    "src.celery_service.ray_serve.s3_backup",
    "src.celery_service.upload_file.video",
    "src.celery_service.upload_file.audio",
    "src.celery_service.openai.excel_agent",
    "src.celery_service.qdrant.embed_task",
    "src.celery_service.qdrant.insertion_task",
],force=True)

celery_app.conf.task_routes = {
    "src.celery_service.openai.embed_task":{"queue":"openai_embedding"},
    "src.celery_service.mongodb.task_status":{"queue":"log_task"},
    "src.celery_service.ray_serve.embed_task":{"queue":"openai_embedding"},
    "src.celery_service.upload_file.video":{"queue":"gemini"},
    "src.celery_service.upload_file.audio":{"queue":"gemini"},
    "src.celery_service.openai.excel_agent":{"queue":"excel_agent"},
    "src.celery_service.qdrant.embed_task":{"queue":"openai_embedding"},
    "src.celery_service.qdrant.insertion_task":{"queue":"qdrant_insertion"},
}

celery_app.conf.update(
    task_track_started=True,
    task_acks_late = True,
    acks_on_failure_or_timeout = False,
    task_expires=DEFAULT_CELERY_TASK_EXP,
    CELERY_TASK_ALWAYS_EAGER=CELERY_TASK_ALWAYS_EAGER,
    CELERY_TASK_REJECT_ON_WORKER_LOST = True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=5,
    broker_transport_options={'visibility_timeout': 300}
)

# celery_app.conf.beat_schedule = {
#     'update-failed-tasks-ttl-every-night': {
#         'task': 'src.celery_service.periodic_task.update_failed_ttl.update_failed_tasks_ttl',
#         'task': 'src.celery_service.periodic_task.gemini_file.delete_old_records',
#         'schedule': crontab(minute=1),
#     },
# }


celery_app.conf.beat_schedule = {
    'delete-gemini-files-after-10-minutes': {
        'task': 'src.celery_service.periodic_task.gemini_file.delete_old_records',
        'schedule': crontab(minute=f'*/{GOOGLE_SCHEDULER_TIME}')
    },
}


# celery_app.conf.beat_schedule.update({
#     'reset-model-usage-every-60-seconds': {
#         'task': 'src.celery_service.periodic_task.reset_usage.model_usage_task',
#         'schedule': 60,
#     },
# })