PRAGMA foreign_keys = OFF;

CREATE TABLE incidents_with_critical_sla (
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
    sla_target_at TEXT,
    resolved_at TEXT,
    closed_at TEXT,
    created_by TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES backoffice_users (id),
    FOREIGN KEY (updated_by) REFERENCES backoffice_users (id)
);

INSERT INTO incidents_with_critical_sla (
    id, title, description, channel, type, severity, responsible_area, status,
    reporter, client_account, created_at, updated_at, sla_target_at, resolved_at,
    closed_at, created_by, updated_by
)
SELECT
    id, title, description, channel, type, severity, responsible_area, status,
    reporter, client_account, created_at, updated_at,
    CASE WHEN severity = 'critical' THEN sla_target_at ELSE NULL END,
    resolved_at, closed_at, created_by, updated_by
FROM incidents;

DROP TABLE incidents;
ALTER TABLE incidents_with_critical_sla RENAME TO incidents;

CREATE INDEX IF NOT EXISTS incidents_filter_index
    ON incidents (status, severity, responsible_area, updated_at);

PRAGMA foreign_keys = ON;
