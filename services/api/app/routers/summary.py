from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.constants import SEVERITIES
from app.dependencies import current_user
from app.schemas import BackofficeUser, SummaryResponse
from app.db import connect
from contextlib import closing

router = APIRouter()


@router.get("/summary", response_model=SummaryResponse)
def summary(_: Annotated[BackofficeUser, Depends(current_user)]) -> SummaryResponse:
    counts = {severity: 0 for severity in SEVERITIES}
    with closing(connect()) as connection:
        rows = connection.execute(
            "SELECT severity, COUNT(*) AS count FROM incidents WHERE status != 'closed' GROUP BY severity"
        ).fetchall()
    for row in rows:
        counts[row["severity"]] = row["count"]
    return SummaryResponse(open_incident_counts_by_severity=counts)
