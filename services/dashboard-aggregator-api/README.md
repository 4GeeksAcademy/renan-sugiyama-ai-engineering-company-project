# Dashboard Aggregator API

Static mock data for `uis/backoffice/dashboard`. No database, authentication,
upstream services, or real aggregation.

## Run locally

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

- `GET /dashboard`: returns `{ "metrics": [...], "panels": [...] }`, matching
  the dashboard's existing mock values and camelCase field names.
- `GET /health`: returns `{ "status": "ok" }`.
- `/docs`: interactive API documentation.

Browser requests are allowed from `http://localhost:4173` and
`http://127.0.0.1:4173`. The frontend is not connected to this service yet.
