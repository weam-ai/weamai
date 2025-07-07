#!/bin/sh

# entrypoint.sh

# Start the Celery worker
celery -A src.celery_worker_hub.import_worker.celery_app worker -Q upload_stream_to_s3,upload_zip_file,extract_and_transform_openai,bulk_update_task,extract_and_transform_anthropic -c 3 --loglevel=info
