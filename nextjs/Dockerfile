# Base stage: install pnpm globally
FROM node:20-alpine AS base
WORKDIR /usr/src/app
# Install pnpm globally in the base image
RUN npm install -g pnpm
# Stage for installing dependencies
FROM base AS deps
COPY package.json pnpm-lock.yaml ./
# Set the pnpm store location to be inside the app directory
RUN pnpm config set store-dir /usr/src/app/.pnpm-store
# Force a clean install by deleting any store-dir config and installing dependencies
RUN pnpm config delete store-dir
RUN pnpm install --no-frozen-lockfile --store-dir /usr/src/app/.pnpm-store

# Stage for building the app
FROM deps AS builder
ARG NEXT_PUBLIC_SERVER_NODE_API_URL
ARG NEXT_PUBLIC_PYTHON_API_URL
ARG NEXT_PUBLIC_DOMAIN_URL
ARG NEXT_PUBLIC_API_PREFIX
ARG NEXT_PUBLIC_APP_ENVIRONMENT
ARG NEXT_PUBLIC_COMMON_NODE_API_URL
ARG NEXT_PUBLIC_COOKIE_NAME
ARG NEXT_PUBLIC_COOKIE_PASSWORD
ARG NEXT_PUBLIC_AWS_S3_URL
ARG NEXT_PUBLIC_HTTPS_PROTOCOL
ARG NEXT_PUBLIC_IMAGE_DOMAIN
ARG NEXT_PUBLIC_SOCKET_CONNECTION_URL
ARG NEXT_PUBLIC_SECURITY_KEY
ARG NEXT_PUBLIC_MESSAGE_LIMIT
ARG NEXT_PUBLIC_FREE_TRIAL_DAYS
ARG NEXT_PUBLIC_OPENAI_PLATFORM_URL
ARG NEXT_PUBLIC_FRESHDESK_SUPPORT_URL
ARG CSRF_TOKEN_SECRET

ENV NEXT_PUBLIC_SERVER_NODE_API_URL=$NEXT_PUBLIC_SERVER_NODE_API_URL
ENV NEXT_PUBLIC_PYTHON_API_URL=$NEXT_PUBLIC_PYTHON_API_URL
ENV NEXT_PUBLIC_DOMAIN_URL=$NEXT_PUBLIC_DOMAIN_URL
ENV NEXT_PUBLIC_API_PREFIX=$NEXT_PUBLIC_API_PREFIX
ENV NEXT_PUBLIC_APP_ENVIRONMENT=$NEXT_PUBLIC_APP_ENVIRONMENT
ENV NEXT_PUBLIC_COMMON_NODE_API_URL=$NEXT_PUBLIC_COMMON_NODE_API_URL
ENV NEXT_PUBLIC_COOKIE_NAME=$NEXT_PUBLIC_COOKIE_NAME
ENV NEXT_PUBLIC_COOKIE_PASSWORD=$NEXT_PUBLIC_COOKIE_PASSWORD
ENV NEXT_PUBLIC_AWS_S3_URL=$NEXT_PUBLIC_AWS_S3_URL
ENV NEXT_PUBLIC_HTTPS_PROTOCOL=$NEXT_PUBLIC_HTTPS_PROTOCOL
ENV NEXT_PUBLIC_IMAGE_DOMAIN=$NEXT_PUBLIC_IMAGE_DOMAIN
ENV NEXT_PUBLIC_SOCKET_CONNECTION_URL=$NEXT_PUBLIC_SOCKET_CONNECTION_URL
ENV NEXT_PUBLIC_SECURITY_KEY=$NEXT_PUBLIC_SECURITY_KEY
ENV NEXT_PUBLIC_MESSAGE_LIMIT=$NEXT_PUBLIC_MESSAGE_LIMIT
ENV NEXT_PUBLIC_FREE_TRIAL_DAYS=$NEXT_PUBLIC_FREE_TRIAL_DAYS
ENV NEXT_PUBLIC_OPENAI_PLATFORM_URL=$NEXT_PUBLIC_OPENAI_PLATFORM_URL
ENV NEXT_PUBLIC_FRESHDESK_SUPPORT_URL=$FRESHDESK_SUPPORT_URL
ENV CSRF_TOKEN_SECRET=$CSRF_TOKEN_SECRET

WORKDIR /usr/src/app
COPY . .
# Make sure TypeScript dependencies are installed
COPY --from=deps /usr/src/app/node_modules ./node_modules
RUN pnpm build
# Final stage for running the application
FROM node:20-alpine
WORKDIR /usr/src/app
# :white_check_mark: Install pnpm again in the final stage to avoid "pnpm: not found"
RUN npm install -g pnpm
ENV NODE_ENV=production

# Copy the necessary files from the builder stage
COPY --from=builder /usr/src/app/next.config.js ./
COPY --from=builder /usr/src/app/public ./public
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/package.json ./package.json

EXPOSE 3000
# Command to start the app
CMD ["npm","start"]






