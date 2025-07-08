FROM node:20-alpine

RUN npm install -g pnpm
RUN apk add --no-cache make gcc g++ python3
COPY package.json pnpm-lock.yaml ./
COPY .npmrc ./
RUN pnpm install
RUN npm rebuild bcrypt --build-from-source
RUN apk del make gcc g++ python3

WORKDIR /usr/src/app
COPY . .
EXPOSE 4050
CMD ["npm", "start"]