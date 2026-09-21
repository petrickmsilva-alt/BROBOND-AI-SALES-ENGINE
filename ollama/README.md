# Ollama

Local LLM runtime used by the API for lead qualification.

- Exposed on port `11434`.
- The entrypoint starts `ollama serve` and pulls `OLLAMA_MODEL` (default `llama3.2`) on first boot.
- Models are persisted in the `ollama_data` volume, so the pull happens only once.

Manual commands:

```bash
docker compose exec ollama ollama list
docker compose exec ollama ollama pull mistral
curl http://localhost:11434/api/tags
```
