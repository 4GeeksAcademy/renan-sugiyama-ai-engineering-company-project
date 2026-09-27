CREATE TABLE IF NOT EXISTS inventory_movements (
    id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('incoming_stock', 'outgoing_stock', 'stock_adjustment')),
    quantity REAL NOT NULL CHECK (quantity > 0),
    reason TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    unit TEXT NOT NULL CHECK (unit IN ('unit', 'pack', 'box', 'ream', 'roll', 'liter', 'kg')),
    direction TEXT CHECK (direction IS NULL OR direction IN ('increase', 'decrease')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES inventory_items (id),
    CHECK (
        (type = 'stock_adjustment' AND direction IS NOT NULL)
        OR (type <> 'stock_adjustment' AND direction IS NULL)
    )
);

CREATE INDEX IF NOT EXISTS inventory_movements_item_index
    ON inventory_movements (item_id, recorded_at, id);
