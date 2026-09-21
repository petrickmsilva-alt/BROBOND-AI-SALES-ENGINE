# BROBOND AI SALES ENGINE

Enterprise SaaS infrastructure for AI-assisted sales: lead capture, automated qualification with a
local LLM, and workflow automation.

[![Stack](https://img.shields.io/badge/Python-3.13-3776AB)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D)](https://redis.io/)

---

## Table of contents

- [Architecture](#architecture)
- [Services](#services)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment variables](#environment-variables)
- [Database migrations](#database-migrations)
- [API reference](#api-reference)
- [Local development](#local-development)
- [Testing](#testing)
- [Code quality](#code-quality)
- [Project structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Architecture

The API follows **Clean Architecture**: dependencies point inwards and the domain layer knows
nothing about frameworks, HTTP, or the database.

```
┌───────────────────────────────────────────────────────────┐
│  api/app/api            HTTP layer (FastAPI routers, DI)  │
├───────────────────────────────────────────────────────────┤
│  api/app/application    Use cases, DTOs (Pydantic)        │
├───────────────────────────────────────────────────────────┤
│  api/app/domain         Entities + repository ports       │
├───────────────────────────────────────────────────────────┤
│  api/app/infrastructure Adapters: SQLAlchemy, Redis, LLM  │
└───────────────────────────────────────────────────────────┘
```

Ports (`domain/repositories`) are abstract; adapters (`infrastructure/`) implement them and are
injected in `api/dependencies.py`. Swapping Ollama for another provider means writing one new
`AIGateway` implementation — no change to routes or use cases.

```
Browser ──▶ Next.js (3000) ──▶ FastAPI (8000) ──┬──▶ PostgreSQL 16 (5432)
                                                 ├──▶ Redis 7 (6379)
                                                 └──▶ Ollama (11434)
                            n8n (5678) ──────────┘
```

---

## Services

| Service    | Port    | Image / build     | Persistence     | Purpose                         |
| ---------- | ------- | ----------------- | --------------- | ------------------------------- |
| `frontend` | `3000`  | `./frontend`      | —               | Next.js 15 App Router dashboard |
| `api`      | `8000`  | `./api`           | —               | FastAPI REST API + Swagger      |
| `postgres` | `5432`  | `postgres:16`     | `postgres_data` | Primary datastore               |
| `redis`    | `6379`  | `redis:7-alpine`  | `redis_data`    | Cache / queue (AOF enabled)     |
| `n8n`      | `5678`  | `n8nio/n8n`       | `n8n_data`      | Workflow automation             |
| `ollama`   | `11434` | `ollama/ollama`   | `ollama_data`   | Local LLM inference             |

---

## Requirements

- Docker Engine 24+ and Docker Compose v2
- 8 GB RAM minimum (the LLM model pull needs headroom)
- ~10 GB free disk space

For local development outside Docker: Python 3.13+ and Node.js 22+.

---

## Installation

```bash
# 1. Clone
git clone https://github.com/petrickmsilva-alt/BROBOND-AI-SALES-ENGINE.git
cd BROBOND-AI-SALES-ENGINE

# 2. Create your environment file
cp .env.example .env

# 3. Generate a strong JWT secret and put it in .env
openssl rand -hex 32

# 4. Build and start the whole stack
docker compose up -d --build

# 5. Follow the logs until every service is healthy
docker compose ps
```

> On the first run Ollama downloads the `llama3.2` model (a few GB). The API stays available while
> the download runs; `/health` reports `ollama: down` until it finishes.

Database migrations are applied automatically by the API container entrypoint
(`alembic upgrade head`) before Uvicorn starts.

### Verify the installation

```bash
./scripts/smoke-test.sh
```

This runs every acceptance check: API `/health`, Swagger, frontend, PostgreSQL, Redis, n8n and
Ollama. Or verify manually:

| What         | URL                                                            |
| ------------ | -------------------------------------------------------------- |
| Frontend     | <http://localhost:3000>                                        |
| API health   | <http://localhost:8000/health>                                 |
| Swagger UI   | <http://localhost:8000/docs>                                   |
| ReDoc        | <http://localhost:8000/redoc>                                  |
| OpenAPI JSON | <http://localhost:8000/openapi.json>                           |
| n8n          | <http://localhost:5678>                                        |
| Ollama       | <http://localhost:11434/api/tags>                              |

A healthy API responds:

```json
{
  "status": "healthy",
  "service": "BROBOND AI Sales Engine",
  "version": "0.1.0",
  "environment": "local",
  "dependencies": { "database": "up", "redis": "up", "ollama": "up" }
}
```

### Common commands

```bash
make up        # build + start everything
make down      # stop
make logs      # tail logs
make ps        # service status
make migrate   # run migrations manually
make smoke     # run smoke tests
make lint      # lint API + frontend
make clean     # stop and delete volumes (destroys data)
```

---

## Environment variables

Every variable lives in [`.env.example`](.env.example). Copy it to `.env` and override as needed.

| Variable                          | Default                          | Description                          |
| --------------------------------- | -------------------------------- | ------------------------------------ |
| `APP_ENV`                         | `local`                          | `local`/`development`/`staging`/`production` |
| `DEBUG`                           | `false`                          | Verbose logging and SQL echo         |
| `API_PORT`                        | `8000`                           | Host port for the API                |
| `FRONTEND_PORT`                   | `3000`                           | Host port for Next.js                |
| `POSTGRES_USER` / `_PASSWORD` / `_DB` | `brobond`                    | Database credentials                 |
| `DATABASE_URL`                    | `postgresql+asyncpg://…`         | Async SQLAlchemy DSN                 |
| `REDIS_URL`                       | `redis://redis:6379/0`           | Redis DSN                            |
| `OLLAMA_BASE_URL`                 | `http://ollama:11434`            | LLM endpoint                         |
| `OLLAMA_MODEL`                    | `llama3.2`                       | Model pulled on first boot           |
| `N8N_ENCRYPTION_KEY`              | `change-me-…`                    | **Change in production**             |
| `JWT_SECRET_KEY`                  | `change-me-in-production`        | **Change in production**             |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                             | Access token lifetime                |
| `CORS_ORIGINS`                    | `["http://localhost:3000"]`      | JSON array of allowed origins        |
| `API_INTERNAL_URL`                | `http://api:8000`                | Used by the frontend server runtime  |

> **Security:** never commit `.env`. Rotate `JWT_SECRET_KEY`, `N8N_ENCRYPTION_KEY` and
> `POSTGRES_PASSWORD` before any deployment.

---

## Database migrations

Alembic runs against the async engine and reads its URL from application settings.

```bash
# Apply all migrations
docker compose exec api alembic upgrade head

# Create a new revision from model changes
docker compose exec api alembic revision --autogenerate -m "add opportunities table"

# Roll back one revision
docker compose exec api alembic downgrade -1

# Detect model/schema drift
docker compose exec api alembic check
```

Initial schema (`0001_initial_schema`): `users` and `leads`.

---

## API reference

Interactive docs: <http://localhost:8000/docs>

| Method | Endpoint                        | Auth | Description                    |
| ------ | ------------------------------- | ---- | ------------------------------ |
| `GET`  | `/health`                       | No   | Service + dependency health    |
| `GET`  | `/`                             | No   | Service metadata               |
| `POST` | `/api/v1/auth/register`         | No   | Create an account              |
| `POST` | `/api/v1/auth/login`            | No   | Obtain access/refresh tokens   |
| `GET`  | `/api/v1/auth/me`               | Yes  | Current user profile           |
| `POST` | `/api/v1/leads`                 | Yes  | Create a lead                  |
| `GET`  | `/api/v1/leads`                 | Yes  | List leads (paginated)         |
| `POST` | `/api/v1/leads/{id}/qualify`    | Yes  | Score the lead with the LLM    |

### Example flow

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"ana@brobond.ai","full_name":"Ana Souza","password":"supersecret123","role":"admin"}'

# Login and capture the token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ana@brobond.ai","password":"supersecret123"}' | jq -r .access_token)

# Create a lead
curl -X POST http://localhost:8000/api/v1/leads \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Carlos Lima","email":"carlos@acme.com","company":"ACME Corp","source":"website"}'

# Qualify it with AI
curl -X POST http://localhost:8000/api/v1/leads/<LEAD_ID>/qualify \
  -H "Authorization: Bearer $TOKEN"
```

Authentication uses JWT bearer tokens (HS256). Passwords are hashed with bcrypt.

---

## Local development

### API

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
```

The frontend reaches the API through a server-side proxy at `/api/backend/*`, controlled by
`API_INTERNAL_URL`. Browser code therefore never needs to know the API host.

---

## Testing

```bash
# API unit tests
cd api && pytest -q

# Full stack acceptance tests
./scripts/smoke-test.sh
```

---

## Code quality

| Layer    | Tools                                  |
| -------- | -------------------------------------- |
| API      | Ruff (lint + import sort), Black, mypy |
| Frontend | ESLint (flat config), Prettier, tsc    |

```bash
make lint     # check everything
make format   # auto-fix
```

Strict type hints are required across the API; `ANN` rules are enforced by Ruff.

---

## Project structure

```
brobond-ai-sales/
├── api/                      FastAPI service (Clean Architecture)
│   ├── app/
│   │   ├── api/              Routers, DI composition root
│   │   ├── application/      Use cases and DTOs
│   │   ├── core/             Config, security, logging, exceptions
│   │   ├── domain/           Entities and repository ports
│   │   └── infrastructure/   SQLAlchemy, Redis, Ollama adapters
│   ├── alembic/              Migrations
│   ├── tests/                Pytest suite
│   └── Dockerfile            Multi-stage build
├── frontend/                 Next.js 15 App Router
│   ├── src/app/              Routes and API proxy
│   ├── src/components/       UI components
│   └── Dockerfile            Multi-stage build (standalone output)
├── n8n/workflows/            Importable automation workflows
├── postgres/init/            Bootstrap SQL
├── redis/redis.conf          Redis configuration (AOF)
├── ollama/entrypoint.sh      Serve + auto-pull model
├── scripts/smoke-test.sh     Acceptance checks
├── docs/                     Architecture and deployment docs
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## Troubleshooting

**`/health` reports `ollama: down`** — the model is still downloading. Watch progress with
`docker compose logs -f ollama`. The API remains usable; only `/qualify` fails.

**`/health` reports `database: down`** — check `docker compose logs postgres` and confirm
`POSTGRES_*` values in `.env` match `DATABASE_URL`.

**Port already in use** — change the `*_PORT` variable in `.env` and run `docker compose up -d`
again.

**Migrations fail on boot** — the API waits for the Postgres healthcheck, but if the database was
initialised with different credentials, reset it with `docker compose down -v` (this deletes data).

**Frontend shows every dependency as unreachable** — confirm the API container is healthy with
`docker compose ps` and that `API_INTERNAL_URL` points at `http://api:8000`.

---

## License

Proprietary — BROBOND.
