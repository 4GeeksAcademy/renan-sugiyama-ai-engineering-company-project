from __future__ import annotations

from contextlib import closing
from typing import Annotated

from fastapi import Header, HTTPException, status
from pydantic import BaseModel

from app.db import connect


class InventoryUser(BaseModel):
    id: str
    role: str


def inventory_manager_user(
    x_inventory_user: Annotated[str | None, Header()] = None,
) -> InventoryUser:
    if not x_inventory_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inventory user is required",
        )

    with closing(connect()) as connection:
        user = connection.execute(
            "SELECT id, role FROM inventory_users WHERE id = ? AND active = 1",
            (x_inventory_user,),
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inventory-manager role required",
        )

    return InventoryUser(id=user["id"], role=user["role"])
