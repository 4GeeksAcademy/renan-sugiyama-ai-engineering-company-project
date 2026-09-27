CREATE TABLE IF NOT EXISTS inventory_users (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK (role = 'inventory-manager'),
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);