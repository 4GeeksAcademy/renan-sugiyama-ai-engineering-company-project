from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from app.constants import DATABASE_PATH
from app.schemas import AuditEventResponse, IncidentResponse


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with closing(connect()) as connection:
        migrations_dir = Path(__file__).parent.parent / "migrations"
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        for migration in sorted(migrations_dir.glob("*.sql")):
            if connection.execute(
                "SELECT 1 FROM schema_migrations WHERE name = ?", (migration.name,)
            ).fetchone():
                continue
            connection.executescript(migration.read_text(encoding="utf-8"))
            connection.execute(
                "INSERT INTO schema_migrations (name, applied_at) VALUES (?, ?)",
                (migration.name, utc_now()),
            )
        connection.commit()


def row_to_incident(row: sqlite3.Row) -> IncidentResponse:
    return IncidentResponse(**dict(row))


def audit_rows(connection: sqlite3.Connection, incident_id: str) -> list[AuditEventResponse]:
    rows = connection.execute(
        "SELECT * FROM audit_events WHERE incident_id = ? ORDER BY occurred_at ASC",
        (incident_id,),
    ).fetchall()
    return [AuditEventResponse(**dict(row)) for row in rows]
