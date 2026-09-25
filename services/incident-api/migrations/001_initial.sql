CREATE TABLE IF NOT EXISTS backoffice_users (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK (role = 'backoffice'),
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    name TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('phone', 'email', 'web_chat')),
    type TEXT NOT NULL CHECK (type IN ('technical_issue', 'access_account_issue', 'billing_issue', 'service_request', 'information_request', 'complaint', 'security_privacy_issue')),
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    responsible_area TEXT NOT NULL CHECK (responsible_area IN ('marketing_and_communications', 'sales_and_business_development', 'human_resources_internal', 'talent_selection_operations', 'corporate_training', 'customer_support_outsourced', 'technology_and_infrastructure', 'executive_direction')),
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'pending_customer', 'escalated', 'resolved', 'closed', 'reopened')),
    reporter TEXT NOT NULL,
    client_account TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    sla_target_at TEXT NOT NULL,
    resolved_at TEXT,
    closed_at TEXT,
    created_by TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES backoffice_users (id),
    FOREIGN KEY (updated_by) REFERENCES backoffice_users (id)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('status_changed', 'responsible_area_changed')),
    actor_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    previous_value TEXT NOT NULL,
    new_value TEXT NOT NULL,
    reason TEXT,
    correlation_id TEXT NOT NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents (id)
);

CREATE INDEX IF NOT EXISTS incidents_filter_index
    ON incidents (status, severity, responsible_area, updated_at);

CREATE INDEX IF NOT EXISTS audit_events_incident_index
    ON audit_events (incident_id, occurred_at);