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
ARG HTTPS_PROTOCOL
ARG IMAGE_DOMAIN
ARG BACKEND_API_URL
ARG COMMON_NODE_API_URL
ARG SERVER_NODE_API_URL
ARG NEXT_PUBLIC_COOKIE_PASSWORD
ARG NEXT_PUBLIC_SECURITY_KEY
ARG NEXT_PUBLIC_API_PREFIX
ARG NEXT_PUBLIC_PYTHON_API_URL
ARG NEXT_PUBLIC_SOCKET_CONNECTION_URL
  # Log the values (for visibility in build logs)
  RUN echo "🚀 BACKEND=$BACKEND_API_URL" && \
  echo "🌐 COMMON=$COMMON_NODE_API_URL" && \
  echo "🧠 SERVER=$SERVER_NODE_API_URL"

ENV NEXT_PUBLIC_HTTPS_PROTOCOL=$HTTPS_PROTOCOL
ENV NEXT_PUBLIC_IMAGE_DOMAIN=$IMAGE_DOMAIN
ENV NEXT_PUBLIC_BACKEND_API_URL=$BACKEND_API_URL
ENV NEXT_PUBLIC_COMMON_NODE_API_URL=$COMMON_NODE_API_URL
ENV SERVER_NODE_API_URL=$SERVER_NODE_API_URL
ENV NEXT_PUBLIC_COOKIE_PASSWORD=$NEXT_PUBLIC_COOKIE_PASSWORD
ENV NEXT_PUBLIC_SECURITY_KEY=$NEXT_PUBLIC_SECURITY_KEY
ENV NEXT_PUBLIC_API_PREFIX=$NEXT_PUBLIC_API_PREFIX
ENV NEXT_PUBLIC_PYTHON_API_URL=$NEXT_PUBLIC_PYTHON_API_URL
ENV NEXT_PUBLIC_SOCKET_CONNECTION_URL=$NEXT_PUBLIC_SOCKET_CONNECTION_URL

env google_env = "osdfijs"

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






