CREATE TABLE IF NOT EXISTS inventory_items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'unit' CHECK (unit IN ('unit', 'pack', 'box', 'ream', 'roll', 'liter', 'kg')),
    reorder_point REAL CHECK (reorder_point IS NULL OR reorder_point >= 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    archived_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS inventory_items_active_index
    ON inventory_items (active, name);
