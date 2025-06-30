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

### 🐞 Debug Mode

Use this mode for debugging with verbose logs and support for IDE tools.

```bash
docker-compose -f docker-compose-enterprise-debugger.yml --env-file .env_enterprise_debug up --build
```

- Enables hot reloading and debug-level logging.
- Suitable for stepping through code or testing integrations.

---

### 📦 Qdrant Vector Store

Start the Qdrant vector database service independently.

```bash
docker-compose -f docker-compose-qdrant.yml up --build
```

- Required for vector similarity search.
- Can be run standalone or alongside the enterprise stack.

---

> 💡 **Pro Tip**: Use a `Makefile` or shell scripts to simplify these commands into easy-to-run shortcuts.
