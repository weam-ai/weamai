#!/bin/bash

# Starting the Ray service
nohup bash -c "ray start --address=ray_head:${RAY_HEAD_NODE_PORT} --redis-password=${RAY_REDIS_PASSWORD} --block"
# nohup ray start --address=ray_head:6385 --block > ray_service.log 2>&1 &
# celery -A celery_service.celery_worker worker --loglevel=info
# echo "python3 model started"

# python3 model_deployment_4.py
