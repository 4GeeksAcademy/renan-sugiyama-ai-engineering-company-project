from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.constants import SEVERITIES, SLA_HOURS, TRANSITIONS
from app.db import initialize_database
from app.routers import catalogs, health, incidents, summary

# re-exported for backward compatibility with services/api/tests/test_contracts.py
__all__ = ["app", "TRANSITIONS", "SEVERITIES", "SLA_HOURS"]

app = FastAPI(title="Nexova Incident API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "X-Backoffice-User"],
)

app.include_router(health.router)
app.include_router(catalogs.router)
app.include_router(incidents.router)
app.include_router(summary.router)


@app.on_event("startup")
def startup() -> None:
    initialize_database()
