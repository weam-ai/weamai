#!/bin/sh

# entrypoint.sh

# Start the Celery worker
celery -A src.celery_worker_hub.web_scraper.celery_app worker -Q scrapsite,upload_file_s3 -c 4 --loglevel=info
