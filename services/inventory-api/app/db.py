from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from app.constants import DATABASE_PATH
from app.schemas import InventoryItemResponse, InventoryMovementResponse

MOVEMENT_STOCK_DELTA_SQL = """
CASE
    WHEN movement.type = 'incoming_stock' THEN movement.quantity
    WHEN movement.type = 'outgoing_stock' THEN -movement.quantity
    WHEN movement.direction = 'increase' THEN movement.quantity
    ELSE -movement.quantity
END
"""

INVENTORY_ITEM_SELECT = f"""
SELECT inventory_items.*,
       (
           SELECT CASE WHEN COUNT(*) = 0 THEN NULL
                       ELSE SUM({MOVEMENT_STOCK_DELTA_SQL})
                  END
           FROM inventory_movements AS movement
           WHERE movement.item_id = inventory_items.id
       ) AS current_stock
FROM inventory_items
"""


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
            applied = connection.execute(
                "SELECT 1 FROM schema_migrations WHERE name = ?", (migration.name,)
            ).fetchone()
            if applied:
                continue
            connection.executescript(migration.read_text(encoding="utf-8"))
            connection.execute(
                "INSERT INTO schema_migrations (name, applied_at) VALUES (?, ?)",
                (migration.name, utc_now()),
            )
        connection.commit()


def row_to_inventory_item(row: sqlite3.Row) -> InventoryItemResponse:
    item = dict(row)
    item["active"] = bool(item["active"])
    return InventoryItemResponse(**item)


def row_to_inventory_movement(row: sqlite3.Row) -> InventoryMovementResponse:
    return InventoryMovementResponse(**dict(row))
