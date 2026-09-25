# Incident API

Centralized FastAPI backend for Nexova's Customer Support incident manager.

## Run locally

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The SQLite database is created at `services/api/data/incidents.db` by default. Set `INCIDENT_DB_PATH` to use another location. The initial schema is in [`migrations/001_initial.sql`](./migrations/001_initial.sql).

All incident endpoints require an `X-Backoffice-User` header whose value exists as an active user in the `backoffice_users` table. For local development, insert a user after the first startup with `INSERT INTO backoffice_users (id, role) VALUES ('local-user', 'backoffice');`. User provisioning belongs to the authenticated identity layer and is intentionally not exposed as an incident API action.

The service records status and responsible-area changes in an append-only audit table inside the same SQLite transaction as the incident update. Audit history is retained by the database; deletion is not exposed through the API.

## Test

```bash
PYTHONPATH=. pytest
```
