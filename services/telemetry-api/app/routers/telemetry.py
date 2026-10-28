import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from jsonschema import Draft7Validator, FormatChecker
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, ValidationError
from psycopg import Error as PsycopgError
from psycopg_pool import PoolClosed, PoolTimeout

from ..db import insert_telemetry_rows

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telemetry")
EVENT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "event-schemas.json"
with EVENT_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
    EVENT_SCHEMA = json.load(schema_file)
EVENT_VALIDATOR = Draft7Validator(EVENT_SCHEMA, format_checker=FormatChecker())


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


EVENT_SERVICE_BY_TYPE: dict[TelemetryEventType, str | None] = {
    TelemetryEventType.WEBSITE_VISIT_RECORDED: "website",
    TelemetryEventType.MARKETING_CONVERSION_COMPLETED: None,
    TelemetryEventType.SALES_CRM_COVERAGE_SNAPSHOT_RECORDED: None,
    TelemetryEventType.EMPLOYEE_DEPARTURE_RECORDED: None,
    TelemetryEventType.WORKFORCE_SNAPSHOT_RECORDED: None,
    TelemetryEventType.EMPLOYEE_ABSENCE_RECORDED: None,
    TelemetryEventType.INTERNAL_REQUISITION_OPENED: None,
    TelemetryEventType.INTERNAL_ROLE_FILLED: None,
    TelemetryEventType.SUPPORT_TICKET_RESOLVED: None,
    TelemetryEventType.SUPPORT_QUEUE_SNAPSHOT_RECORDED: None,
    TelemetryEventType.SUPPORT_QUERY_CLOSED: None,
    TelemetryEventType.SUPPORT_DISSATISFACTION_DETECTED: None,
    TelemetryEventType.SUPPORT_TICKET_ESCALATED: None,
    TelemetryEventType.DEPARTMENT_KPI_SNAPSHOT_RECORDED: None,
    TelemetryEventType.KPI_THRESHOLD_TRIGGERED: None,
    TelemetryEventType.USER_AUTHENTICATION_DENIED: "auth",
    TelemetryEventType.STOCK_MOVEMENT_VALIDATION_FAILED: "inventory",
    TelemetryEventType.DIRECT_STOCK_EDIT_REJECTED: None,
    TelemetryEventType.OUTBOUND_STOCK_BLOCKED: "inventory",
    TelemetryEventType.STOCK_MOVEMENT_RECORDED: "inventory",
    TelemetryEventType.STOCK_THRESHOLD_TRIGGERED: "inventory",
    TelemetryEventType.STOCK_MOVEMENT_CORRECTION_RECORDED: None,
    TelemetryEventType.API_LATENCY_RECORDED: "inventory",
    TelemetryEventType.API_REQUEST_FAILED: "inventory",
}

EVENT_LEVEL_BY_TYPE: dict[TelemetryEventType, Literal["info", "error"]] = {
    TelemetryEventType.WEBSITE_VISIT_RECORDED: "info",
    TelemetryEventType.MARKETING_CONVERSION_COMPLETED: "info",
    TelemetryEventType.SALES_CRM_COVERAGE_SNAPSHOT_RECORDED: "info",
    TelemetryEventType.EMPLOYEE_DEPARTURE_RECORDED: "info",
    TelemetryEventType.WORKFORCE_SNAPSHOT_RECORDED: "info",
    TelemetryEventType.EMPLOYEE_ABSENCE_RECORDED: "info",
    TelemetryEventType.INTERNAL_REQUISITION_OPENED: "info",
    TelemetryEventType.INTERNAL_ROLE_FILLED: "info",
    TelemetryEventType.SUPPORT_TICKET_RESOLVED: "info",
    TelemetryEventType.SUPPORT_QUEUE_SNAPSHOT_RECORDED: "info",
    TelemetryEventType.SUPPORT_QUERY_CLOSED: "info",
    TelemetryEventType.SUPPORT_DISSATISFACTION_DETECTED: "info",
    TelemetryEventType.SUPPORT_TICKET_ESCALATED: "info",
    TelemetryEventType.DEPARTMENT_KPI_SNAPSHOT_RECORDED: "info",
    TelemetryEventType.KPI_THRESHOLD_TRIGGERED: "info",
    TelemetryEventType.USER_AUTHENTICATION_DENIED: "error",
    TelemetryEventType.STOCK_MOVEMENT_VALIDATION_FAILED: "error",
    TelemetryEventType.DIRECT_STOCK_EDIT_REJECTED: "error",
    TelemetryEventType.OUTBOUND_STOCK_BLOCKED: "error",
    TelemetryEventType.STOCK_MOVEMENT_RECORDED: "info",
    TelemetryEventType.STOCK_THRESHOLD_TRIGGERED: "info",
    TelemetryEventType.STOCK_MOVEMENT_CORRECTION_RECORDED: "info",
    TelemetryEventType.API_LATENCY_RECORDED: "info",
    TelemetryEventType.API_REQUEST_FAILED: "error",
}


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(alias="eventId")
    timestamp: AwareDatetime
    session_id: UUID = Field(alias="sessionId")
    user_id: str = Field(alias="userId", min_length=1)
    event_type: TelemetryEventType
    schema_version: Literal["2.0.0"] = Field(alias="schemaVersion")
    request_id: UUID = Field(alias="requestId")
    properties: dict[str, Any]


def map_event_to_row(event: TelemetryEvent) -> dict[str, Any]:
    properties = event.model_dump(mode="json", include={"properties"})["properties"]
    value = properties.pop("value", None)
    message = properties.pop("message", None)
    tags = dict(properties)
    tags["event_id"] = str(event.event_id)
    return {
        "event_type": event.event_type.value,
        "timestamp": event.timestamp,
        "service": EVENT_SERVICE_BY_TYPE[event.event_type],
        "tags": tags,
        "level": EVENT_LEVEL_BY_TYPE[event.event_type],
        "value": value,
        "message": message,
    }


class TelemetryBatch(BaseModel):
    events: list[Any]


@router.post("/events")
def receive_events(batch: TelemetryBatch, request: Request) -> dict[str, int]:
    rejected = 0
    valid_events = []
    for raw_event in batch.events:
        try:
            event = TelemetryEvent.model_validate(raw_event)
            EVENT_VALIDATOR.validate(raw_event)
        except (ValidationError, JsonSchemaValidationError):
            rejected += 1
            continue
        valid_events.append(event)

    rows = [map_event_to_row(event) for event in valid_events]

    try:
        stored = insert_telemetry_rows(request.app.state.telemetry_pool, rows)
    except (PsycopgError, PoolClosed, PoolTimeout) as error:
        logger.error("Telemetry batch persistence failed")
        raise HTTPException(
            status_code=503,
            detail="Telemetry persistence unavailable",
        ) from error

    rejected += len(rows) - stored
    logger.info(
        "Processed %d telemetry events; stored %d; rejected %d",
        len(batch.events),
        stored,
        rejected,
    )
    for row in rows:
        logger.info("Telemetry event_type: %s", row["event_type"])

    return {
        "received": len(batch.events),
        "stored": stored,
        "rejected": rejected,
    }