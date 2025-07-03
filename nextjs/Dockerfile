# Base stage: install pnpm globally
FROM node:20-alpine AS base
WORKDIR /usr/src/app

# # Install pnpm globally in the base image
# RUN npm install -g pnpm

# # Stage for installing dependencies
# FROM base AS deps
# COPY package.json pnpm-lock.yaml ./

# # Set the pnpm store location to be inside the app directory
# RUN pnpm config set store-dir /usr/src/app/.pnpm-store

# # Force a clean install by deleting any store-dir config and installing dependencies
# RUN pnpm config delete store-dir
# RUN pnpm install --no-frozen-lockfile --store-dir /usr/src/app/.pnpm-store

# # Stage for building the app
# FROM deps AS builder
# ARG HTTPS_PROTOCOL
# ARG IMAGE_DOMAIN
# ARG BACKEND_API_URL

# ENV NEXT_PUBLIC_HTTPS_PROTOCOL=$HTTPS_PROTOCOL
# ENV NEXT_PUBLIC_IMAGE_DOMAIN=$IMAGE_DOMAIN
# ENV NEXT_PUBLIC_BACKEND_API_URL=$BACKEND_API_URL

# WORKDIR /usr/src/app
# COPY . .

# # Make sure TypeScript dependencies are installed
# # RUN pnpm install --save-dev @types/react @types/node --store-dir /usr/src/app/.pnpm-store

# RUN pnpm build

# # Final stage for running the application
# FROM node:20-alpine
# WORKDIR /usr/src/app

# # ✅ Install pnpm again in the final stage to avoid "pnpm: not found"
# RUN npm install -g pnpm

# # Copy the necessary files from the builder stage
# COPY --from=builder /usr/src/app/next.config.js ./
# COPY --from=builder /usr/src/app/public ./public
# COPY --from=builder /usr/src/app/.next ./.next
# COPY --from=builder /usr/src/app/node_modules ./node_modules
# COPY --from=builder /usr/src/app/package.json ./package.json


RUN npm install -g pnpm
# RUN apk add --no-cache make gcc g++ python3
COPY package.json pnpm-lock.yaml ./
# COPY .npmrc ./
RUN pnpm install
# RUN apk del make gcc g++ python3

WORKDIR /usr/src/app
COPY . .



# Expose the app on port 3000
EXPOSE 3000

# Command to start the app
CMD ["pnpm", "run","dev"]
