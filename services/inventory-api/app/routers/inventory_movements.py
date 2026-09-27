from __future__ import annotations

import sqlite3
from contextlib import closing
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.db import connect, row_to_inventory_movement, utc_now
from app.dependencies import inventory_manager_user
from app.schemas import (
    InventoryMovementCreate,
    InventoryMovementResponse,
    validate_movement_unit,
)

router = APIRouter(
    prefix="/inventory/movements",
    tags=["inventory-movements"],
    dependencies=[Depends(inventory_manager_user)],
)


def movement_delta(movement: InventoryMovementCreate) -> float:
    if movement.type == "incoming_stock":
        return movement.quantity
    if movement.type == "outgoing_stock":
        return -movement.quantity
    return movement.quantity if movement.direction == "increase" else -movement.quantity


@router.post("", response_model=InventoryMovementResponse, status_code=status.HTTP_201_CREATED)
def register_movement(payload: InventoryMovementCreate) -> InventoryMovementResponse:
    with closing(connect()) as connection:
        try:
            connection.execute("BEGIN IMMEDIATE")
            item = connection.execute(
                "SELECT unit FROM inventory_items WHERE id = ? AND active = 1",
                (payload.item_id,),
            ).fetchone()
            if item is None:
                connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventory item not found",
                )

            try:
                validate_movement_unit(item["unit"], payload.unit)
            except ValueError as error:
                connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(error),
                ) from error

            current_stock = connection.execute(
                """
                SELECT COALESCE(SUM(
                    CASE
                        WHEN type = 'incoming_stock' THEN quantity
                        WHEN type = 'outgoing_stock' THEN -quantity
                        WHEN direction = 'increase' THEN quantity
                        ELSE -quantity
                    END
                ), 0) AS current_stock
                FROM inventory_movements
                WHERE item_id = ?
                """,
                (payload.item_id,),
            ).fetchone()["current_stock"]

            if current_stock + movement_delta(payload) < 0:
                connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Movement would produce negative stock",
                )

            movement_id = str(uuid4())
            created_at = utc_now()
            connection.execute(
                """
                INSERT INTO inventory_movements (
                    id, item_id, type, quantity, reason, recorded_at,
                    unit, direction, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    movement_id,
                    payload.item_id,
                    payload.type,
                    payload.quantity,
                    payload.reason,
                    payload.recorded_at.isoformat(),
                    payload.unit,
                    payload.direction,
                    created_at,
                ),
            )
            connection.commit()
            row = connection.execute(
                "SELECT * FROM inventory_movements WHERE id = ?",
                (movement_id,),
            ).fetchone()
        except HTTPException:
            raise
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Movement could not be persisted",
            ) from error

    return row_to_inventory_movement(row)