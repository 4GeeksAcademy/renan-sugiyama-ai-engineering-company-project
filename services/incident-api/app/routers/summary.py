from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from app.constants import SLA_HOURS, SEVERITIES
from app.dependencies import current_user
from app.schemas import BackofficeUser, SummaryResponse
from app.db import connect
from contextlib import closing

router = APIRouter()


@router.get("/summary", response_model=SummaryResponse)
def summary(_: Annotated[BackofficeUser, Depends(current_user)]) -> SummaryResponse:
    counts = {severity: 0 for severity in SEVERITIES}
    now = datetime.now(timezone.utc).isoformat()
    with closing(connect()) as connection:
        rows = connection.execute(
            "SELECT severity, COUNT(*) AS count FROM incidents WHERE status != 'closed' GROUP BY severity"
        ).fetchall()
        metrics = connection.execute(
            """
            SELECT
                SUM(CASE WHEN status != 'closed' THEN 1 ELSE 0 END) AS open_backlog_count,
                SUM(CASE WHEN status != 'closed' AND sla_target_at IS NOT NULL
                    AND sla_target_at < ? THEN 1 ELSE 0 END)
                    AS overdue_open_incident_count,
                AVG(CASE WHEN resolved_at IS NOT NULL
                    THEN (julianday(resolved_at) - julianday(created_at)) * 24 END)
                    AS average_resolution_hours,
                SUM(CASE WHEN resolved_at IS NOT NULL AND sla_target_at IS NOT NULL
                    AND resolved_at <= sla_target_at
                    THEN 1 ELSE 0 END) AS resolved_within_sla_count,
                SUM(CASE WHEN resolved_at IS NOT NULL AND sla_target_at IS NOT NULL THEN 1 ELSE 0 END)
                    AS resolved_count
            FROM incidents
            """,
            (now,),
        ).fetchone()
    for row in rows:
        counts[row["severity"]] = row["count"]
    resolved_count = metrics["resolved_count"] or 0
    resolved_within_sla_percent = (
        round(metrics["resolved_within_sla_count"] * 100 / resolved_count, 1)
        if resolved_count
        else None
    )
    return SummaryResponse(
        open_incident_counts_by_severity=counts,
        open_backlog_count=metrics["open_backlog_count"] or 0,
        overdue_open_incident_count=metrics["overdue_open_incident_count"] or 0,
        sla_hours=SLA_HOURS,
        average_resolution_hours=(
            round(metrics["average_resolution_hours"], 1)
            if metrics["average_resolution_hours"] is not None
            else None
        ),
        resolved_within_sla_percent=resolved_within_sla_percent,
    )
