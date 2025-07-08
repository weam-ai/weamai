#!/bin/bash
# build.sh
# Step 1: Build the pybase_image using the pybase_docker service
echo ":hammer: Step 1: Building pybase_image via docker-compose service pybase_docker..."
docker compose build pybase_docker --no-cache
set -e
# Load and export all .env variables
set -a
source .env
set +a
# Convert all .env keys into --build-arg flags
BUILD_ARGS=$(grep -v '^#' .env | sed '/^\s*$/d' | awk -F= '{print "--build-arg " $1}')
# Build the image
echo ":hammer: Step 2: Building weamai-app (Next.js frontend)..."
docker build $BUILD_ARGS -f ./nextjs/Dockerfile -t weamai-app:latest ./nextjs --no-cache
