#!/bin/sh

# entrypoint.sh

# Start the Celery worker
celery -A src.celery_worker_hub.extraction.celery_app worker -Q extraction --loglevel=info
