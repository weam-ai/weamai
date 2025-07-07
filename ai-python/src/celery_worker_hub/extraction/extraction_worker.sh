#!/bin/sh

# entrypoint.sh

# Start the Celery worker
celery -A src.celery_worker_hub.extraction.celery_app worker -Q extraction -c 3 --loglevel=info
