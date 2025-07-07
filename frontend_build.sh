#!/bin/bash
# build.sh

set -e

# Load and export all .env variables
set -a
source .env
set +a

# Convert all .env keys into --build-arg flags
BUILD_ARGS=$(grep -v '^#' .env | sed '/^\s*$/d' | awk -F= '{print "--build-arg " $1}')

# Build the image
docker build $BUILD_ARGS -f ./nextjs/Dockerfile -t weamai-app:latest ./nextjs --no-cache
