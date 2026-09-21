# n8n

Automation layer that orchestrates lead intake and AI qualification.

- UI: http://localhost:5678
- Workflows are mounted read-only at `/workflows` inside the container.
- State is stored in PostgreSQL (database `n8n`) and the `n8n_data` volume.

## Importing the sample workflow

```bash
docker compose exec n8n n8n import:workflow --input=/workflows/lead-qualification.json
```

The sample workflow exposes a webhook (`POST /webhook/brobond-lead`) that creates a lead in the
API and then triggers AI qualification.
