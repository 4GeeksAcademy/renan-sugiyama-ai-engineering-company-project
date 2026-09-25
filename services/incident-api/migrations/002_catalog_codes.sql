PRAGMA foreign_keys = OFF;

ALTER TABLE incidents RENAME TO incidents_legacy;
ALTER TABLE audit_events RENAME TO audit_events_legacy;

CREATE TABLE incidents (
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

CREATE TABLE audit_events (
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

INSERT INTO incidents (
    id, title, description, channel, type, severity, responsible_area, status,
    reporter, client_account, created_at, updated_at, sla_target_at, resolved_at,
    closed_at, created_by, updated_by
)
SELECT
    id, title, description,
    CASE channel WHEN 'web chat' THEN 'web_chat' ELSE channel END,
    CASE type
        WHEN 'Technical issue' THEN 'technical_issue'
        WHEN 'Access/account issue' THEN 'access_account_issue'
        WHEN 'Billing issue' THEN 'billing_issue'
        WHEN 'Service request' THEN 'service_request'
        WHEN 'Information request' THEN 'information_request'
        WHEN 'Complaint' THEN 'complaint'
        WHEN 'Security/privacy issue' THEN 'security_privacy_issue'
        ELSE type
    END,
    lower(severity),
    CASE responsible_area
        WHEN 'Marketing and Communications' THEN 'marketing_and_communications'
        WHEN 'Sales and Business Development' THEN 'sales_and_business_development'
        WHEN 'Human Resources (Internal)' THEN 'human_resources_internal'
        WHEN 'Talent Selection Operations (core business)' THEN 'talent_selection_operations'
        WHEN 'Corporate Training' THEN 'corporate_training'
        WHEN 'Customer Support (outsourced service)' THEN 'customer_support_outsourced'
        WHEN 'Technology and Infrastructure' THEN 'technology_and_infrastructure'
        WHEN 'Executive Direction' THEN 'executive_direction'
        ELSE responsible_area
    END,
    CASE status
        WHEN 'Open' THEN 'open'
        WHEN 'In progress' THEN 'in_progress'
        WHEN 'Pending customer' THEN 'pending_customer'
        WHEN 'Escalated' THEN 'escalated'
        WHEN 'Resolved' THEN 'resolved'
        WHEN 'Closed' THEN 'closed'
        WHEN 'Reopened' THEN 'reopened'
        ELSE status
    END,
    reporter, client_account, created_at, updated_at, sla_target_at, resolved_at,
    closed_at, created_by, updated_by
FROM incidents_legacy;

INSERT INTO audit_events (
    id, incident_id, event_type, actor_id, occurred_at, previous_value, new_value,
    reason, correlation_id
)
SELECT
    id, incident_id, event_type, actor_id, occurred_at,
    CASE
        WHEN event_type = 'status_changed' AND previous_value = 'Open' THEN 'open'
        WHEN event_type = 'status_changed' AND previous_value = 'In progress' THEN 'in_progress'
        WHEN event_type = 'status_changed' AND previous_value = 'Pending customer' THEN 'pending_customer'
        WHEN event_type = 'status_changed' AND previous_value = 'Escalated' THEN 'escalated'
        WHEN event_type = 'status_changed' AND previous_value = 'Resolved' THEN 'resolved'
        WHEN event_type = 'status_changed' AND previous_value = 'Closed' THEN 'closed'
        WHEN event_type = 'status_changed' AND previous_value = 'Reopened' THEN 'reopened'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Marketing and Communications' THEN 'marketing_and_communications'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Sales and Business Development' THEN 'sales_and_business_development'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Human Resources (Internal)' THEN 'human_resources_internal'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Talent Selection Operations (core business)' THEN 'talent_selection_operations'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Corporate Training' THEN 'corporate_training'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Customer Support (outsourced service)' THEN 'customer_support_outsourced'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Technology and Infrastructure' THEN 'technology_and_infrastructure'
        WHEN event_type = 'responsible_area_changed' AND previous_value = 'Executive Direction' THEN 'executive_direction'
        ELSE previous_value
    END,
    CASE
        WHEN event_type = 'status_changed' AND new_value = 'Open' THEN 'open'
        WHEN event_type = 'status_changed' AND new_value = 'In progress' THEN 'in_progress'
        WHEN event_type = 'status_changed' AND new_value = 'Pending customer' THEN 'pending_customer'
        WHEN event_type = 'status_changed' AND new_value = 'Escalated' THEN 'escalated'
        WHEN event_type = 'status_changed' AND new_value = 'Resolved' THEN 'resolved'
        WHEN event_type = 'status_changed' AND new_value = 'Closed' THEN 'closed'
        WHEN event_type = 'status_changed' AND new_value = 'Reopened' THEN 'reopened'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Marketing and Communications' THEN 'marketing_and_communications'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Sales and Business Development' THEN 'sales_and_business_development'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Human Resources (Internal)' THEN 'human_resources_internal'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Talent Selection Operations (core business)' THEN 'talent_selection_operations'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Corporate Training' THEN 'corporate_training'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Customer Support (outsourced service)' THEN 'customer_support_outsourced'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Technology and Infrastructure' THEN 'technology_and_infrastructure'
        WHEN event_type = 'responsible_area_changed' AND new_value = 'Executive Direction' THEN 'executive_direction'
        ELSE new_value
    END,
    reason, correlation_id
FROM audit_events_legacy;

DROP TABLE audit_events_legacy;
DROP TABLE incidents_legacy;

CREATE INDEX IF NOT EXISTS incidents_filter_index
    ON incidents (status, severity, responsible_area, updated_at);

CREATE INDEX IF NOT EXISTS audit_events_incident_index
    ON audit_events (incident_id, occurred_at);

PRAGMA foreign_keys = ON;