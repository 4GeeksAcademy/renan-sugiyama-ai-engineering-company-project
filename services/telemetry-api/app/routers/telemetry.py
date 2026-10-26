import logging
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telemetry")


class TelemetryEventType(str, Enum):
    WEBSITE_VISIT_RECORDED = "website_visit_recorded"
    MARKETING_CONVERSION_COMPLETED = "marketing_conversion_completed"
    SALES_CRM_COVERAGE_SNAPSHOT_RECORDED = "sales_crm_coverage_snapshot_recorded"
    EMPLOYEE_DEPARTURE_RECORDED = "employee_departure_recorded"
    WORKFORCE_SNAPSHOT_RECORDED = "workforce_snapshot_recorded"
    EMPLOYEE_ABSENCE_RECORDED = "employee_absence_recorded"
    INTERNAL_REQUISITION_OPENED = "internal_requisition_opened"
    INTERNAL_ROLE_FILLED = "internal_role_filled"
    SUPPORT_TICKET_RESOLVED = "support_ticket_resolved"
    SUPPORT_QUEUE_SNAPSHOT_RECORDED = "support_queue_snapshot_recorded"
    SUPPORT_QUERY_CLOSED = "support_query_closed"
    SUPPORT_DISSATISFACTION_DETECTED = "support_dissatisfaction_detected"
    SUPPORT_TICKET_ESCALATED = "support_ticket_escalated"
    DEPARTMENT_KPI_SNAPSHOT_RECORDED = "department_kpi_snapshot_recorded"
    KPI_THRESHOLD_TRIGGERED = "kpi_threshold_triggered"
    USER_AUTHENTICATION_DENIED = "user_authentication_denied"
    STOCK_MOVEMENT_VALIDATION_FAILED = "stock_movement_validation_failed"
    DIRECT_STOCK_EDIT_REJECTED = "direct_stock_edit_rejected"
    OUTBOUND_STOCK_BLOCKED = "outbound_stock_blocked"
    STOCK_MOVEMENT_RECORDED = "stock_movement_recorded"
    STOCK_THRESHOLD_TRIGGERED = "stock_threshold_triggered"
    STOCK_MOVEMENT_CORRECTION_RECORDED = "stock_movement_correction_recorded"
    API_LATENCY_RECORDED = "api_latency_recorded"
    API_REQUEST_FAILED = "api_request_failed"


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(alias="eventId")
    timestamp: AwareDatetime
    session_id: UUID = Field(alias="sessionId")
    user_id: str = Field(alias="userId", min_length=1)
    event_type: TelemetryEventType
    schema_version: Literal["1.0.0"] = Field(alias="schemaVersion")
    request_id: UUID = Field(alias="requestId")
    properties: dict[str, Any]


class TelemetryBatch(BaseModel):
    events: list[TelemetryEvent]


@router.post("/events")
def receive_events(batch: TelemetryBatch) -> dict[str, int]:
    logger.info("Received %d telemetry events", len(batch.events))
    for event in batch.events:
        logger.info("Telemetry event_type: %s", event.event_type.value)

    return {"received": len(batch.events)}