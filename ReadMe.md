# IoT Device Management Backend

A FastAPI backend for managing IoT devices, user authentication (JWT-based), telemetry data, and status dashboards.

---

## 🚀 Features

- User registration and login with JWT authentication
- CRUD for devices
- Telemetry ingestion and retrieval
- Device state updates
- Rate limiting (SlowAPI)
- Swagger docs with Bearer Token Auth
- PostgreSQL with SQLAlchemy
- Production-ready CI/CD using GitHub Actions

---

## 🚀 Deployment Recommendation

Since I haven't used Azure before, I can't confidently suggest any service from Azure.

### ✅ AWS Options

#### Custom Deployment:
- Use an **EC2 instance** or a cluster depending on expected traffic.
- You'll need to manage:
  - Load balancing
  - Deployment automation
  - Logging and monitoring
  - Metrics collection
  - High availability

#### Managed Deployment:
- **Elastic Beanstalk** is a great choice for:
  - Built-in load balancing and scaling
  - Easy GitHub-based or ZIP file deployments
  - Minimal ops overhead

---

## 🛠️ Updates for Production-Ready FastAPI

To make your FastAPI backend production-ready:

- ❌ Remove `Base.metadata.create_all()` and `drop_all()` from `main.py` to avoid data loss.
- ✅ Use **Alembic** for database migrations and schema management.
- ✅ Load all configs from `.env` or use a **cloud secrets manager**.
- ✅ Add **structured logging** and **metrics config** (e.g., with `loguru`, `prometheus`, or Gunicorn logs).
- ✅ Use multiple **Gunicorn/Uvicorn workers** and disable `debug=True`.
- ✅ Add **CORS middleware** if your API will be accessed by external frontends.

---

## 🔁 CI/CD Pipeline

### ✅ GitHub Actions

Create a pipeline in `.github/workflows/pipeline.yml` that includes:

- ✅ Dependency installation (`pip install`)
- ✅ Database service setup (e.g., PostgreSQL or SQLite for testing)
- ✅ Running unit/integration tests with `pytest`
- ✅ Deployment step (e.g., using AWS Elastic Beanstalk CLI or SSH to EC2)

> 📌 Use GitHub Secrets to store AWS credentials, database URLs, JWT secrets, and other sensitive environment variables.
