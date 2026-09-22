.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help setup up down logs ps build migrate seed smoke smoke-local test contract lint format clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Create .env from the template
	@test -f .env || cp .env.example .env

up: setup ## Start the whole stack
	$(COMPOSE) up -d --build

down: ## Stop the stack
	$(COMPOSE) down

logs: ## Tail all logs
	$(COMPOSE) logs -f

ps: ## Show service status
	$(COMPOSE) ps

build: ## Build all images
	$(COMPOSE) build

migrate: ## Apply database migrations
	$(COMPOSE) exec api alembic upgrade head

seed: ## Seed the database with demo CRM data
	$(COMPOSE) exec api python -m app.seed

test: ## Run API unit tests with coverage
	cd api && python -m pytest

contract: ## Run API contract tests (OpenAPI snapshot + endpoint contracts)
	cd api && python -m pytest tests/contracts

smoke: ## Run the HTTP smoke test against the running stack
	python scripts/smoke.py

smoke-local: ## Run the legacy shell smoke test against the running stack
	./scripts/smoke-test.sh

lint: ## Lint and type-check the API and frontend
	cd api && ruff check . && black --check . && mypy app scripts
	cd frontend && npm run lint && npm run format:check

format: ## Auto-format API and frontend
	cd api && ruff check --fix . && black .
	cd frontend && npm run format

clean: ## Stop the stack and drop volumes
	$(COMPOSE) down -v
