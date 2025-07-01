## 🚀 Enterprise Development Setup

This project supports multiple environments using Docker Compose. Use the following commands to build and run each environment.

---

### 🔧 Local Development

Use this setup for day-to-day local development.

```bash
docker-compose -f docker-compose-enterprise-local.yml --env-file .env_enterprise_local up --build
```

- Loads environment variables from `.env_enterprise_local`.
- Builds and starts all enterprise services locally.

---
### 🛠️ Dev Environment

Run the development image to simulate a production-like environment, ideal for pre-deployment checks or CI/CD pipelines.

```bash
docker-compose -f docker-compose-enterprise-dev.yml --env-file .env_enterprise_dev up --build
```

- Uses `.env_enterprise_dev` for environment variables.
- Builds and runs services as they would appear in staging or production.

---


