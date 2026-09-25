from __future__ import annotations

from contextlib import closing
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.db import connect
from app.schemas import BackofficeUser


def current_user(x_backoffice_user: Annotated[str | None, Header()] = None) -> BackofficeUser:
    if not x_backoffice_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Backoffice user is required")
    with closing(connect()) as connection:
        user = connection.execute(
            "SELECT id, role FROM backoffice_users WHERE id = ? AND active = 1",
            (x_backoffice_user,),
        ).fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Assigned backoffice role required")
    return BackofficeUser(id=user["id"], role=user["role"])
