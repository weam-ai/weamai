#!/bin/sh

# entrypoint.sh

# Start the Celery worker
celery -A src.celery_service.celery_worker  worker -Q openai_embedding,qdrant_insertion,log_task,excel_agent -c 10 --pool=gevent &

celery -A src.celery_service.celery_worker  worker -Q celery,gemini -c 2 -B
