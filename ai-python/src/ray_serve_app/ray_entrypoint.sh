#!/bin/bash

# Get the IP address using hostname command
IP_ADDRESS=$(hostname -i)

ray metrics launch-prometheus &
# Run ray start command with the obtained IP address
sleep 5

ray start \
    --head \
    --port=${RAY_HEAD_NODE_PORT} \
    --node-manager-port=${RAY_NODE_MANAGER_PORT} \
    --object-manager-port=${RAY_OBEJECT_MANAGER_PORT} \
    --include-dashboard=true \
    --dashboard-host=${RAY_SERVE_HOST} \
    --dashboard-port=${RAY_DASHBOARD} \
    --node-ip-address=${IP_ADDRESS} \
    --metrics-export-port=${RAY_METRICS_EXPORT_PORT} \
    --redis-password=${RAY_REDIS_PASSWORD} \
    --block & \
    
sleep 10
echo "python3 model started"

python3 ray_serve_app/web.py