# 🚀 Open Source Development Setup

This project supports multiple environments using Docker Compose. Use the commands below to build and run each environment.

---

## 🔧 Local Development

Use this setup for day-to-day development on your local machine.

```bash
docker-compose -f docker-compose-local.yml --env-file .env_local up --build
# or
docker-compose -f docker-compose-local.yml --env-file .env up --build
```

- Loads environment variables from `.env_local` or `.env`.
- Builds and starts all core services locally.
- Ideal for active feature development and testing.

---

## 🛠️ Development (CI/CD or Pre-Prod)

Use this environment to simulate a production-like setup. It's suitable for CI/CD pipelines, integration testing, or pre-deployment checks.

```bash
docker-compose -f docker-compose-dev.yml --env-file .env_dev up --build
```

- Loads variables from `.env_dev`.
- Builds and runs services with production-ready configurations.
- Ideal for automated testing or team-level staging environments.
