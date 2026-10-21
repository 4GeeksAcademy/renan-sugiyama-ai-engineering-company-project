from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.constants import CHANNELS, INCIDENT_TYPES, RESPONSIBLE_AREAS, SEVERITIES, STATUSES
from app.dependencies import current_user
from app.schemas import BackofficeUser, IncidentCatalogsResponse

router = APIRouter()


@router.get("/catalogs", response_model=IncidentCatalogsResponse)
def catalogs(_: Annotated[BackofficeUser, Depends(current_user)]) -> IncidentCatalogsResponse:
    return IncidentCatalogsResponse(
        channels=CHANNELS,
        types=INCIDENT_TYPES,
        severities=SEVERITIES,
        statuses=STATUSES,
        responsible_areas=RESPONSIBLE_AREAS,
    )
