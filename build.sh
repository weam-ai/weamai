#!/bin/bash
# build.sh

# Step 1: Build the pybase_image using the pybase_docker service
echo " 🔨 Step 1: Building pybase_image via docker-compose service pybase_docker..."
docker compose build pybase_docker --no-cache

set -e
# Load and export all .env variables
set -a
source .env
set +a

# Determine build target based on NEXT_PUBLIC_APP_ENVIRONMENT
TARGET="production"  # default
if [ "$NEXT_PUBLIC_APP_ENVIRONMENT" == "development" ]; then
  TARGET="development"
fi

echo "🛠️ Building target: $TARGET based on NEXT_PUBLIC_APP_ENVIRONMENT=$NEXT_PUBLIC_APP_ENVIRONMENT"


# Convert all .env keys into --build-arg flags
BUILD_ARGS=$(grep -v '^#' .env | sed '/^\s*$/d' | awk -F= '{print "--build-arg " $1}')
# Build the image
echo "🔨 Step 2: Building weamai-app (Next.js frontend)..."
docker build $BUILD_ARGS \
  --target=$TARGET \
  -f ./nextjs/Dockerfile \
  -t weamai-app:latest \
  ./nextjs --no-cache

