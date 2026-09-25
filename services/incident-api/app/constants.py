from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

DATABASE_PATH = Path(os.getenv("INCIDENT_DB_PATH", "services/incident-api/data/incidents.db"))
SLA_HOURS = 24

CHANNELS = ("phone", "email", "web_chat")
INCIDENT_TYPES = (
    "technical_issue",
    "access_account_issue",
    "billing_issue",
    "service_request",
    "information_request",
    "complaint",
    "security_privacy_issue",
)
SEVERITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "in_progress", "pending_customer", "escalated", "resolved", "closed", "reopened")
RESPONSIBLE_AREAS = (
    "marketing_and_communications",
    "sales_and_business_development",
    "human_resources_internal",
    "talent_selection_operations",
    "corporate_training",
    "customer_support_outsourced",
    "technology_and_infrastructure",
    "executive_direction",
)
TRANSITIONS = {
    "open": ("in_progress", "escalated"),
    "in_progress": ("open", "pending_customer", "escalated", "resolved"),
    "pending_customer": ("in_progress", "resolved"),
    "escalated": ("open", "in_progress", "resolved"),
    "resolved": ("in_progress", "pending_customer", "escalated", "closed", "reopened"),
    "closed": ("reopened",),
    "reopened": ("in_progress", "resolved"),
}

Channel = Literal["phone", "email", "web_chat"]
IncidentType = Literal[
    "technical_issue", "access_account_issue", "billing_issue", "service_request",
    "information_request", "complaint", "security_privacy_issue",
]
Severity = Literal["critical", "high", "medium", "low"]
IncidentStatus = Literal[
    "open", "in_progress", "pending_customer", "escalated", "resolved", "closed", "reopened",
]
ResponsibleArea = Literal[
    "marketing_and_communications", "sales_and_business_development", "human_resources_internal",
    "talent_selection_operations", "corporate_training", "customer_support_outsourced",
    "technology_and_infrastructure", "executive_direction",
]
