.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help setup up down logs ps build migrate smoke test lint format clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

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

smoke: ## Run the end-to-end smoke tests
	./scripts/smoke-test.sh

test: ## Run API unit tests
	cd api && python -m pytest -q

lint: ## Lint API and frontend
	cd api && ruff check . && black --check .
	cd frontend && npm run lint && npm run format:check

format: ## Auto-format API and frontend
	cd api && ruff check --fix . && black .
	cd frontend && npm run format

clean: ## Stop the stack and drop volumes
	$(COMPOSE) down -v
