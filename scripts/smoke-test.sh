#!/usr/bin/env bash
# Validates every service required by PR001 acceptance criteria.
set -uo pipefail

API_PORT="${API_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
N8N_PORT="${N8N_PORT:-5678}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
POSTGRES_USER="${POSTGRES_USER:-brobond}"
POSTGRES_DB="${POSTGRES_DB:-brobond}"

failures=0

check() {
  local name="$1"
  shift
  printf '%-28s' "$name"
  if "$@" >/dev/null 2>&1; then
    printf 'PASS\n'
  else
    printf 'FAIL\n'
    failures=$((failures + 1))
  fi
}

wait_for_http() {
  local url="$1" attempts="${2:-60}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 5
  done
  return 1
}

echo "Waiting for the stack to become available..."
wait_for_http "http://localhost:${API_PORT}/health" 60

echo
echo "BROBOND AI SALES ENGINE - smoke tests"
echo "-------------------------------------"
check "API /health"          curl -fsS "http://localhost:${API_PORT}/health"
check "API Swagger /docs"    curl -fsS "http://localhost:${API_PORT}/docs"
check "API openapi.json"     curl -fsS "http://localhost:${API_PORT}/openapi.json"
check "Frontend"             wait_for_http "http://localhost:${FRONTEND_PORT}" 24
check "PostgreSQL"           docker compose exec -T postgres pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"
check "Redis"                docker compose exec -T redis redis-cli ping
check "n8n"                  wait_for_http "http://localhost:${N8N_PORT}/healthz" 24
check "Ollama"               wait_for_http "http://localhost:${OLLAMA_PORT}/api/tags" 24
echo "-------------------------------------"

if [ "$failures" -eq 0 ]; then
  echo "All smoke tests passed."
  exit 0
fi

echo "$failures smoke test(s) failed."
exit 1
