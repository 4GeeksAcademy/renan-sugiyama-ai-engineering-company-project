from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.constants import Channel, IncidentType, ResponsibleArea, Severity, IncidentStatus


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    channel: Channel
    type: IncidentType
    severity: Severity
    responsible_area: ResponsibleArea
    reporter: str = Field(min_length=1)
    client_account: str | None = None


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    channel: Channel | None = None
    type: IncidentType | None = None
    severity: Severity | None = None
    reporter: str | None = Field(default=None, min_length=1)
    client_account: str | None = None


class AssignmentChange(BaseModel):
    responsible_area: ResponsibleArea
    reason: str | None = None


class StatusChange(BaseModel):
    status: IncidentStatus
    reason: str | None = None


class BackofficeUser(BaseModel):
    id: str
    role: Literal["backoffice"]


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    channel: Channel
    type: IncidentType
    severity: Severity
    responsible_area: ResponsibleArea
    status: IncidentStatus
    reporter: str
    client_account: str | None
    created_at: str
    updated_at: str
    sla_target_at: str
    resolved_at: str | None
    closed_at: str | None
    created_by: str
    updated_by: str


class AuditEventResponse(BaseModel):
    id: str
    incident_id: str
    event_type: Literal["status_changed", "responsible_area_changed"]
    actor_id: str
    occurred_at: str
    previous_value: str
    new_value: str
    reason: str | None
    correlation_id: str


class IncidentDetailResponse(BaseModel):
    incident: IncidentResponse
    audit_history: list[AuditEventResponse]


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    page: int
    page_size: int
    total_items: int
    total_pages: int


class SummaryResponse(BaseModel):
    open_incident_counts_by_severity: dict[str, int]
