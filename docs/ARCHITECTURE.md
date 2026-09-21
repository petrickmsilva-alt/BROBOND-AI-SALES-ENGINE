# Architecture

## Principles

The API is organised with **Clean Architecture** and the **SOLID** principles. The dependency rule
is enforced: outer layers depend on inner layers, never the reverse.

| Layer            | Package                  | Knows about                        | Must not know about        |
| ---------------- | ------------------------ | ---------------------------------- | -------------------------- |
| Domain           | `app/domain`             | Nothing external                   | FastAPI, SQLAlchemy, Redis |
| Application      | `app/application`        | Domain                             | FastAPI, SQLAlchemy        |
| Infrastructure   | `app/infrastructure`     | Domain (implements its ports)      | FastAPI routes             |
| Interface (HTTP) | `app/api`                | Application + Infrastructure (DI)  | —                          |

## Layers

### Domain (`app/domain`)

Framework-free business model.

- `entities/user.py` — `User` aggregate with `UserRole`.
- `entities/lead.py` — `Lead` aggregate; `apply_score()` holds the qualification rule
  (score must be 0–100; a score ≥ 50 promotes the lead to `QUALIFIED`).
- `repositories/` — abstract **ports**: `UserRepository`, `LeadRepository`, `AIGateway`.

### Application (`app/application`)

Use cases that orchestrate the domain, plus the Pydantic DTOs that define the API contract.

- `AuthService` — registration (rejects duplicates) and login (issues a JWT pair).
- `LeadService` — CRUD plus `qualify()`, which builds the prompt, calls the `AIGateway` port and
  persists the result.
- `HealthService` — aggregates dependency status; never raises, always reports.

### Infrastructure (`app/infrastructure`)

Concrete **adapters** implementing the domain ports.

- `repositories/` — SQLAlchemy 2 async implementations, mapping ORM models to entities.
- `models/` — declarative ORM mappings (the persistence shape, separate from entities).
- `cache/redis_client.py` — shared async Redis client.
- `llm/ollama_gateway.py` — `AIGateway` implementation talking to Ollama, with defensive parsing
  of the model's JSON output.

### Interface (`app/api`)

- `dependencies.py` is the **composition root**: it builds repositories and services and injects
  them. Routes depend on abstractions resolved here.
- `v1/routes/` — thin routers that translate domain exceptions into HTTP status codes.

## SOLID in practice

- **S** — each service owns one use case; each adapter one integration.
- **O** — a new LLM provider is a new `AIGateway` implementation; nothing else changes.
- **L** — every `UserRepository` implementation honours the same contract, so tests can substitute
  in-memory fakes.
- **I** — ports are small and focused rather than one large repository interface.
- **D** — use cases depend on abstract ports; concretions are injected at the edge.

## Data model

```
users                                leads
─────                                ─────
id            uuid pk                id          uuid pk
email         varchar(320) unique    name        varchar(255)
full_name     varchar(255)           email       varchar(320) idx
hashed_password varchar(255)         company     varchar(255)
role          varchar(32)            phone       varchar(32)
is_active     boolean                source      varchar(64)
created_at    timestamptz            status      varchar(32) idx
updated_at    timestamptz            score       integer
                                     notes       text
                                     owner_id    uuid fk → users.id (ON DELETE SET NULL)
                                     created_at  timestamptz
                                     updated_at  timestamptz
```

## Request flow: lead qualification

1. `POST /api/v1/leads/{id}/qualify` — the bearer token is validated and the `User` resolved.
2. The router calls `LeadService.qualify(lead_id)`.
3. The service loads the lead through `LeadRepository` (raises `EntityNotFoundError` → HTTP 404).
4. It builds a prompt and calls `AIGateway.score_lead()`.
5. `OllamaGateway` posts to `/api/generate` and parses the JSON response defensively.
6. `Lead.apply_score()` enforces the business rule and updates status.
7. The updated lead is persisted and serialised into `LeadScoreResponse`.

## Health checks

`/health` returns HTTP 200 with a body describing each dependency. PostgreSQL and Redis are
treated as critical: if either is down the overall status becomes `degraded`. Ollama is
non-critical, so the service stays `healthy` while a model downloads. The endpoint never raises,
which keeps it usable as a container healthcheck.

## Security

- Passwords hashed with bcrypt (input truncated to bcrypt's 72-byte limit).
- Stateless JWT (HS256) with separate `access` and `refresh` token types; decoding validates the
  expected type, so a refresh token cannot be used as an access token.
- Containers run as non-root users (`appuser` / `nextjs`).
- CORS origins are configured explicitly through settings.
