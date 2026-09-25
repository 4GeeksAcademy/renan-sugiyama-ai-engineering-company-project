from __future__ import annotations

from contextlib import closing
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.constants import SLA_HOURS, TRANSITIONS, ResponsibleArea, Severity, IncidentStatus
from app.db import audit_rows, connect, row_to_incident, utc_now
from app.dependencies import current_user
from app.schemas import (
    AssignmentChange,
    AuditEventResponse,
    BackofficeUser,
    IncidentCreate,
    IncidentDetailResponse,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
    StatusChange,
)

router = APIRouter()


@router.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    user: Annotated[BackofficeUser, Depends(current_user)],
) -> IncidentResponse:
    now = datetime.now(timezone.utc)
    incident_id = str(uuid4())
    values = {
        "id": incident_id,
        **payload.model_dump(),
        "status": "open",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "sla_target_at": (
            (now + timedelta(hours=SLA_HOURS)).isoformat()
            if payload.severity == "critical"
            else None
        ),
        "resolved_at": None,
        "closed_at": None,
        "created_by": user.id,
        "updated_by": user.id,
    }
    columns = ", ".join(values)
    placeholders = ", ".join("?" for _ in values)
    with closing(connect()) as connection:
        connection.execute(
            f"INSERT INTO incidents ({columns}) VALUES ({placeholders})",
            tuple(values.values()),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return row_to_incident(row)


@router.get("/incidents", response_model=IncidentListResponse)
def list_incidents(
    user: Annotated[BackofficeUser, Depends(current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    search: str | None = None,
    status_filter: IncidentStatus | None = Query(default=None, alias="status"),
    severity: Severity | None = None,
    responsible_area: ResponsibleArea | None = None,
    sort_by: Literal["created_at", "updated_at", "severity", "status", "responsible_area"] = "updated_at",
    sort_direction: Literal["asc", "desc"] = "desc",
) -> IncidentListResponse:
    del user
    clauses: list[str] = []
    parameters: list[str] = []
    if search:
        clauses.append("(title LIKE ? OR description LIKE ? OR reporter LIKE ?)")
        term = f"%{search}%"
        parameters.extend([term, term, term])
    for column, value in (("status", status_filter), ("severity", severity), ("responsible_area", responsible_area)):
        if value is not None:
            clauses.append(f"{column} = ?")
            parameters.append(value)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    order = "DESC" if sort_direction == "desc" else "ASC"
    offset = (page - 1) * page_size
    with closing(connect()) as connection:
        total = connection.execute(f"SELECT COUNT(*) FROM incidents{where}", parameters).fetchone()[0]
        rows = connection.execute(
            f"SELECT * FROM incidents{where} ORDER BY {sort_by} {order} LIMIT ? OFFSET ?",
            [*parameters, page_size, offset],
        ).fetchall()
    return IncidentListResponse(
        items=[row_to_incident(row) for row in rows],
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/incidents/{incident_id}", response_model=IncidentDetailResponse)
def get_incident(
    incident_id: str,
    _: Annotated[BackofficeUser, Depends(current_user)],
) -> IncidentDetailResponse:
    with closing(connect()) as connection:
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return IncidentDetailResponse(incident=row_to_incident(row), audit_history=audit_rows(connection, incident_id))


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    user: Annotated[BackofficeUser, Depends(current_user)],
) -> IncidentResponse:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field is required")
    assignments = ", ".join(f"{column} = ?" for column in updates)
    with closing(connect()) as connection:
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        if "severity" in updates:
            if updates["severity"] == "critical" and row["sla_target_at"] is None:
                created_at = datetime.fromisoformat(row["created_at"])
                updates["sla_target_at"] = (created_at + timedelta(hours=SLA_HOURS)).isoformat()
            elif updates["severity"] != "critical":
                updates["sla_target_at"] = None
        updates.update({"updated_at": utc_now(), "updated_by": user.id})
        assignments = ", ".join(f"{column} = ?" for column in updates)
        cursor = connection.execute(
            f"UPDATE incidents SET {assignments} WHERE id = ?",
            [*updates.values(), incident_id],
        )
        connection.commit()
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return row_to_incident(row)


@router.post("/incidents/{incident_id}/assignment", response_model=IncidentResponse)
def assign_incident(
    incident_id: str,
    payload: AssignmentChange,
    user: Annotated[BackofficeUser, Depends(current_user)],
) -> IncidentResponse:
    correlation_id = str(uuid4())
    now = utc_now()
    with closing(connect()) as connection:
        connection.execute("BEGIN")
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        if row["responsible_area"] == payload.responsible_area:
            raise HTTPException(status_code=400, detail="Incident is already assigned to this area")
        connection.execute(
            "UPDATE incidents SET responsible_area = ?, updated_at = ?, updated_by = ? WHERE id = ?",
            (payload.responsible_area, now, user.id, incident_id),
        )
        connection.execute(
            "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(uuid4()), incident_id, "responsible_area_changed", user.id, now,
             row["responsible_area"], payload.responsible_area, payload.reason, correlation_id),
        )
        connection.commit()
        updated = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return row_to_incident(updated)


@router.post("/incidents/{incident_id}/status", response_model=IncidentResponse)
def change_status(
    incident_id: str,
    payload: StatusChange,
    user: Annotated[BackofficeUser, Depends(current_user)],
) -> IncidentResponse:
    correlation_id = str(uuid4())
    now = utc_now()
    with closing(connect()) as connection:
        connection.execute("BEGIN")
        row = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        if payload.status not in TRANSITIONS[row["status"]]:
            raise HTTPException(status_code=409, detail="Invalid incident status transition")
        resolved_at = now if payload.status == "resolved" else row["resolved_at"]
        closed_at = now if payload.status == "closed" else row["closed_at"]
        if payload.status == "reopened":
            resolved_at = None
            closed_at = None
        connection.execute(
            "UPDATE incidents SET status = ?, resolved_at = ?, closed_at = ?, updated_at = ?, updated_by = ? WHERE id = ?",
            (payload.status, resolved_at, closed_at, now, user.id, incident_id),
        )
        connection.execute(
            "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(uuid4()), incident_id, "status_changed", user.id, now,
             row["status"], payload.status, payload.reason, correlation_id),
        )
        connection.commit()
        updated = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return row_to_incident(updated)


@router.get("/incidents/{incident_id}/history", response_model=list[AuditEventResponse])
def get_history(
    incident_id: str,
    _: Annotated[BackofficeUser, Depends(current_user)],
) -> list[AuditEventResponse]:
    with closing(connect()) as connection:
        if connection.execute("SELECT 1 FROM incidents WHERE id = ?", (incident_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return audit_rows(connection, incident_id)
