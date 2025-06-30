import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
load_dotenv()

CELERY_BROKEN_URL = os.environ.get("CELERY_BROKEN_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
SCHEDULER_TIME = int(os.environ.get("SCHEDULER_TIME", 50))
DEFAULT_CELERY_TASK_EXP = os.environ.get("DEFAULT_CELERY_TASK_EXP", 86400)
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", False)

#create Celery instance
celery_app = Celery("web_scraper", broker=CELERY_BROKEN_URL, backend=CELERY_RESULT_BACKEND)
celery_app.autodiscover_tasks(['src.celery_worker_hub.web_scraper.tasks.scrap_url','src.celery_worker_hub.web_scraper.tasks.summary',
                               'src.celery_worker_hub.web_scraper.tasks.db_dump',
                               'src.celery_worker_hub.web_scraper.tasks.notify',
                               "src.celery_worker_hub.web_scraper.periodic_task.update_failed_ttl",
                               'src.celery_worker_hub.web_scraper.tasks.scraping_sitemap',
                               "src.celery_worker_hub.web_scraper.tasks.upload_file_s3"],force=True)
celery_app.conf.task_routes = {"src.celery_worker_hub.web_scraper.tasks.scrap_url": {"queue": "scrapsite"},
                               'src.celery_worker_hub.web_scraper.tasks.summary':{"queue":"scrapsite"},
                               'src.celery_worker_hub.web_scraper.tasks.db_dump':{"queue":"scrapsite"},
                               'src.celery_worker_hub.web_scraper.tasks.notify':{"queue":"scrapsite"},
                                'src.celery_worker_hub.web_scraper.tasks.scraping_sitemap':{"queue":"scrapsite"},
                               "src.celery_worker_hub.web_scraper.tasks.upload_file_s3": {"queue": "upload_file_s3"}}


celery_app.conf.update(
    task_track_started=True,
    task_acks_late = True,
    acks_on_failure_or_timeout = False,
    task_expires=DEFAULT_CELERY_TASK_EXP,
    CELERY_TASK_ALWAYS_EAGER=CELERY_TASK_ALWAYS_EAGER,
    CELERY_TASK_REJECT_ON_WORKER_LOST = True,
    worker_prefetch_multiplier=3,
    worker_max_tasks_per_child=3,
    broker_transport_options={'visibility_timeout': 300}
)

celery_app.conf.beat_schedule = {
    'update-failed-tasks-ttl-every-night': {
        'task': 'src.celery_worker_hub.web_scraper.periodic_task.update_failed_ttl.update_failed_tasks_ttl',
        'schedule': crontab(minute=SCHEDULER_TIME),
    },
}



