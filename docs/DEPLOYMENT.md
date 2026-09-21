# Deployment

## Container images

Both images use **multi-stage builds**.

`api/Dockerfile`
1. `builder` — installs build toolchain and compiles dependencies into `/opt/venv`.
2. `runtime` — `python:3.13-slim` with only the virtualenv, a non-root `appuser`, and a
   `curl`-based `HEALTHCHECK` against `/health`.

`frontend/Dockerfile`
1. `deps` — resolves npm dependencies.
2. `builder` — runs `next build`, producing the `standalone` output.
3. `runtime` — `node:22-alpine` serving `server.js` as the non-root `nextjs` user.

Only the build stages carry compilers and dev dependencies, keeping the runtime images small and
reducing attack surface.

## Startup order

`docker-compose.yml` uses healthcheck-gated `depends_on`:

```
postgres (healthy) ─┬─▶ api ─▶ frontend
redis    (healthy) ─┘
postgres (healthy) ──▶ n8n
```

The API entrypoint runs `alembic upgrade head` before starting Uvicorn, so migrations are always
applied against a database that is already accepting connections.

## Persistence

| Volume          | Mounted at                 | Contents                          |
| --------------- | -------------------------- | --------------------------------- |
| `postgres_data` | `/var/lib/postgresql/data` | Relational data                   |
| `redis_data`    | `/data`                    | AOF + RDB snapshots               |
| `ollama_data`   | `/root/.ollama`            | Downloaded models                 |
| `n8n_data`      | `/home/node/.n8n`          | Workflow credentials and state    |

`docker compose down` keeps volumes; `docker compose down -v` destroys them.

## Production checklist

- [ ] Replace `JWT_SECRET_KEY` with `openssl rand -hex 32`.
- [ ] Replace `N8N_ENCRYPTION_KEY` and `POSTGRES_PASSWORD`.
- [ ] Set `APP_ENV=production` and `DEBUG=false`.
- [ ] Restrict `CORS_ORIGINS` to your real domains.
- [ ] Stop publishing `5432` and `6379` to the host; keep them on the internal network.
- [ ] Terminate TLS at a reverse proxy in front of ports 3000/8000.
- [ ] Enable authentication on n8n and do not expose it publicly without protection.
- [ ] Configure backups for the `postgres_data` volume.
- [ ] Ship container logs to a central aggregator.

## Scaling notes

- The API is stateless and can be replicated horizontally behind a load balancer; tune
  `DATABASE_POOL_SIZE` and `DATABASE_MAX_OVERFLOW` against the Postgres `max_connections` budget.
- Ollama is CPU/GPU bound. For production, run it on dedicated hardware and point
  `OLLAMA_BASE_URL` at that host, or swap in a hosted provider by writing a new `AIGateway`.
- Redis is already configured with `allkeys-lru`, so it can serve as a bounded cache.
