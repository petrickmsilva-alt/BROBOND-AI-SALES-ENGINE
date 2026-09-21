#!/bin/sh
set -e

ollama serve &
server_pid=$!

until ollama list >/dev/null 2>&1; do
  sleep 2
done

model="${OLLAMA_MODEL:-llama3.2}"
if ! ollama list | grep -q "$model"; then
  echo "Pulling model $model"
  ollama pull "$model" || echo "Model pull failed; Ollama still serving"
fi

wait "$server_pid"
