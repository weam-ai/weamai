#!/bin/sh

# entrypoint.sh

# Start the Celery worker
celery -A src.celery_service.celery_worker worker -Q celery,ray_embedding,openai_embedding,qdrant_insertion,gemini,log_task,excel_agent  -B
