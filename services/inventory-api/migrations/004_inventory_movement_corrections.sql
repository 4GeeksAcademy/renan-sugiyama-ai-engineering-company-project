CREATE TABLE IF NOT EXISTS inventory_movement_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL CHECK (event_type = 'InventoryMovementCorrected'),
    original_movement_id TEXT NOT NULL UNIQUE,
    compensating_movement_id TEXT NOT NULL UNIQUE,
    occurred_at TEXT NOT NULL,
    FOREIGN KEY (original_movement_id) REFERENCES inventory_movements (id),
    FOREIGN KEY (compensating_movement_id) REFERENCES inventory_movements (id),
    CHECK (original_movement_id <> compensating_movement_id)
);