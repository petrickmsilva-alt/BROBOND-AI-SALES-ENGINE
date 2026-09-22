# CRM Core

The CRM core (PR002) turns the BROBOND AI Sales Engine into a customer-centric
sales platform. It is built on the same **Clean Architecture** layering as the
rest of the API: `domain` (entities + repository ports), `application`
(use-case services + DTOs), `infrastructure` (SQLAlchemy models + adapters) and
`api` (FastAPI routers).

## Data model

Every record in the CRM revolves around a **Cliente** (customer). Leads,
conversations and sales all belong to a customer.

```
Cliente ─┬─< Lead        (pipeline opportunities)
         ├─< Conversa    (message history)
         └─< Venda        (closed sales)

Produto                    (standalone apparel catalogue)
```

### Cliente

| Field        | Type      | Notes                     |
| ------------ | --------- | ------------------------- |
| `id`         | UUID (PK) | generated                 |
| `nome`       | str       | required                  |
| `telefone`   | str?      |                           |
| `email`      | str?      | indexed                   |
| `instagram`  | str?      |                           |
| `cidade`     | str?      |                           |
| `created_at` | datetime  | server default            |
| `updated_at` | datetime  | server default / onupdate |

### Produto

| Field       | Type          | Notes            |
| ----------- | ------------- | ---------------- |
| `id`        | UUID (PK)     |                  |
| `sku`       | str           | unique, indexed  |
| `nome`      | str           | required         |
| `descricao` | str?          |                  |
| `categoria` | str?          | indexed          |
| `cor`       | str?          |                  |
| `tamanho`   | str?          |                  |
| `preco`     | Decimal(10,2) | `>= 0`           |
| `estoque`   | int           | `>= 0`           |
| `ativo`     | bool          | default `true`   |

### Lead

| Field        | Type            | Notes                         |
| ------------ | --------------- | ----------------------------- |
| `id`         | UUID (PK)       |                               |
| `cliente_id` | UUID (FK)       | → `clientes.id` (CASCADE)     |
| `origem`     | str?            | e.g. `instagram`, `whatsapp`  |
| `score`      | int             | `0–100`, set by AI qualify    |
| `status`     | enum            | pipeline stage (see below)    |
| `interesse`  | str?            |                               |
| `observacao` | str?            |                               |
| `created_at` | datetime        |                               |

**Pipeline status enum:** `novo`, `contato`, `negociacao`, `proposta`,
`fechado`, `perdido`.

### Conversa

| Field        | Type      | Notes                              |
| ------------ | --------- | ---------------------------------- |
| `id`         | UUID (PK) |                                    |
| `cliente_id` | UUID (FK) | → `clientes.id` (CASCADE)          |
| `role`       | enum      | `user`, `assistant`, `system`      |
| `mensagem`   | str       | required                           |
| `created_at` | datetime  |                                    |

### Venda

| Field              | Type          | Notes                                   |
| ------------------ | ------------- | --------------------------------------- |
| `id`               | UUID (PK)     |                                         |
| `cliente_id`       | UUID (FK)     | → `clientes.id` (CASCADE)               |
| `valor`            | Decimal(10,2) | `>= 0`                                  |
| `metodo_pagamento` | enum          | `pix`, `cartao`, `boleto`, `dinheiro`   |
| `status`           | enum          | `pendente`, `pago`, `cancelado`         |
| `created_at`       | datetime      |                                         |

## Endpoints

All CRM endpoints live under the `/api/v1` prefix.

### Clientes

| Method   | Path                    | Description        |
| -------- | ----------------------- | ------------------ |
| `GET`    | `/clientes`             | List (paginated)   |
| `GET`    | `/clientes/{id}`        | Retrieve one       |
| `POST`   | `/clientes`             | Create             |
| `PUT`    | `/clientes/{id}`        | Update (partial)   |
| `DELETE` | `/clientes/{id}`        | Delete (cascade)   |

### Produtos

| Method | Path              | Description      |
| ------ | ----------------- | ---------------- |
| `GET`  | `/produtos`       | List (paginated) |
| `GET`  | `/produtos/{id}`  | Retrieve one     |
| `POST` | `/produtos`       | Create           |
| `PUT`  | `/produtos/{id}`  | Update (partial) |

### Leads

| Method  | Path                     | Description                         |
| ------- | ------------------------ | ----------------------------------- |
| `GET`   | `/leads`                 | List (paginated)                    |
| `GET`   | `/leads/{id}`            | Retrieve one                        |
| `POST`  | `/leads`                 | Create for an existing cliente      |
| `PATCH` | `/leads/{id}/status`     | Move through the pipeline           |
| `POST`  | `/leads/{id}/qualify`    | AI score (Ollama); `200` or `503`   |

### Dashboard

| Method | Path                    | Description                    |
| ------ | ----------------------- | ------------------------------ |
| `GET`  | `/dashboard/pipeline`   | Lead counts per stage          |
| `GET`  | `/dashboard/summary`    | Aggregate CRM metrics          |

`GET /dashboard/pipeline` returns:

```json
{
  "novo": 12,
  "contato": 8,
  "negociacao": 4,
  "proposta": 3,
  "fechado": 9,
  "perdido": 1
}
```

## Migrations

The schema is created exclusively through Alembic — the application never calls
`Base.metadata.create_all()`.

```bash
# inside the api container / environment
alembic upgrade head      # apply
alembic downgrade -1      # roll back the last revision
```

Revisions:

- `0001` – users + placeholder leads (PR001)
- `0002` – CRM core: reshapes `leads`, adds `clientes`, `produtos`,
  `conversas`, `vendas`

With the stack running you can use the Make targets:

```bash
make migrate   # docker compose exec api alembic upgrade head
```

## Seeding

A deterministic seed command populates representative BroBond data:

```bash
python -m app.seed     # inside the api container/environment
make seed              # docker compose exec api python -m app.seed
```

It inserts **20 clientes, 30 produtos, 50 leads and 10 vendas** (plus sample
conversas). The catalogue covers every model — *Camiseta Essential, Oversized,
Polo, Jeans, Moletom* — in the colours *Preto, Branco, Off White, Verde
Militar, Azul Marinho*. The command is idempotent: it is a no-op if the
database already contains customers.

## Testing

```bash
make test       # full unit + integration suite with a 90% coverage gate
make contract   # OpenAPI snapshot + per-endpoint contract tests
make smoke      # HTTP smoke test against a running stack
```

Tests run against a SQLite database provisioned through the real Alembic
migrations (never `create_all`), so the tested schema matches production.
