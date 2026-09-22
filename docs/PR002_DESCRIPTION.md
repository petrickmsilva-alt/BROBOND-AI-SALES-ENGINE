# PR002 — CRM Core + PostgreSQL Schema

Implementa o núcleo do CRM, banco relacional, migrations, repository pattern,
services e testes. Inclui também o endurecimento de contratos da API (PR002.1).

## Escopo

### PR002 — CRM Core

- **Domínio** (Clean Architecture): entidades `Cliente`, `Produto`, `Lead`
  (pipeline `novo → contato → negociacao → proposta → fechado → perdido`),
  `Conversa` (roles `user/assistant/system`) e `Venda` (métodos de pagamento e
  status), com regras de negócio nas entidades e nos serviços.
- **Banco relacional PostgreSQL**: `clientes` 1:N `leads`/`conversas`/`vendas`
  e catálogo `produtos`. Coluna UUID portável (nativa no PostgreSQL, `CHAR(32)`
  no SQLite de teste).
- **Migrations Alembic**: revisão `0002_crm_core` (remodela `leads` e cria
  `clientes`, `produtos`, `conversas`, `vendas`). O app **nunca** usa
  `create_all()`; `env.py` respeita URL injetada pelos testes.
- **Repository Pattern**: portas no domínio + adaptadores SQLAlchemy async
  (`Cliente`, `Produto`, `Lead`, `Venda`, `Conversa`).
- **Service Layer**: `ClienteService`, `ProdutoService`, `LeadService`,
  `DashboardService` — toda a regra de negócio vive aqui.
- **Schemas** separados: Create / Update / Read / List.
- **Rotas REST** (`/api/v1`): CRUD de clientes e produtos, leads com
  `PATCH /leads/{id}/status` e `POST /leads/{id}/qualify` (IA), e
  `GET /dashboard/pipeline` + `GET /dashboard/summary`.
- **Seed** (`python -m app.seed`): 20 clientes, 30 produtos BroBond
  (Camiseta Essential, Oversized, Polo, Jeans, Moletom nas cores Preto, Branco,
  Off White, Verde Militar, Azul Marinho), 50 leads e 10 vendas. Idempotente.
- **Testes** (Pytest): CRUD de clientes e produtos, status de leads, pipeline
  do dashboard, migration e seed. Rodam sobre SQLite provisionado pelas
  migrations reais. Cobertura **≥ 90%** (gate `--cov-fail-under=90`).

### PR002.1 — API Contract Hardening

- **Contract tests** em `tests/contracts/`: `test_clientes_contract.py`,
  `test_leads_contract.py`, `test_dashboard_contract.py` — validam método HTTP,
  status code, schema, OpenAPI e `content-type`.
- **OpenAPI snapshot** (`tests/contracts/openapi_snapshot.json`) comparado com
  `GET /openapi.json`; se um endpoint some, o CI falha. Regeneração explícita
  via `python -m scripts.update_openapi_snapshot`.
- **Smoke** (`scripts/smoke.py`): `/health`, `/clientes`, `/leads`,
  `/dashboard/pipeline` e `/leads/{id}/qualify`. `qualify` responde `200`/`503`,
  **nunca `500`**.
- **CI** (`.github/workflows/ci.yml`): jobs `quality` (ruff → black → mypy →
  pytest) → `contract-tests` → `docker-smoke`.
- **Makefile**: `make test`, `make contract`, `make smoke`, `make seed`,
  `make migrate`.
- **Badges** no README: Build, Coverage, Contracts, Smoke.

## Como validar localmente

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check . && black --check . && mypy app scripts
pytest                     # cobertura >= 90%
pytest tests/contracts     # contratos

# stack completa
make up && make migrate && make seed && make smoke
```

## Notas

- A branch da spec é `feature/PR002-crm-core`; esta sessão está fixada à branch
  `arena/...`, então o PR sai a partir dela.
- Endpoints do CRM estão abertos (sem auth) para viabilizar o smoke; basta
  injetar `CurrentUserDep` num router para exigir bearer token.
