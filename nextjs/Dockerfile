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






