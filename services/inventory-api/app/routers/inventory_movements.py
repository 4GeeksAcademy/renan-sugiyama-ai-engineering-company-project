from __future__ import annotations

import sqlite3
from contextlib import closing
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.db import MOVEMENT_STOCK_DELTA_SQL, connect, row_to_inventory_movement, utc_now
from app.dependencies import inventory_manager_user
from app.schemas import (
    InventoryMovementCorrectedEvent,
    InventoryMovementCorrectionCreate,
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


def compensating_movement(
    original: sqlite3.Row,
    payload: InventoryMovementCorrectionCreate,
) -> InventoryMovementCreate:
    if original["type"] == "incoming_stock":
        movement_type, direction = "outgoing_stock", None
    elif original["type"] == "outgoing_stock":
        movement_type, direction = "incoming_stock", None
    elif original["direction"] == "increase":
        movement_type, direction = "stock_adjustment", "decrease"
    else:
        movement_type, direction = "stock_adjustment", "increase"

    return InventoryMovementCreate(
        item_id=original["item_id"],
        type=movement_type,
        quantity=original["quantity"],
        reason=payload.reason,
        recorded_at=payload.recorded_at,
        unit=original["unit"],
        direction=direction,
    )


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
                f"""
                SELECT COALESCE(SUM({MOVEMENT_STOCK_DELTA_SQL}), 0) AS current_stock
                FROM inventory_movements AS movement
                WHERE movement.item_id = ?
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


@router.post(
    "/{movement_id}/correction",
    response_model=InventoryMovementCorrectedEvent,
    status_code=status.HTTP_201_CREATED,
)
def correct_movement(
    movement_id: str,
    payload: InventoryMovementCorrectionCreate,
) -> InventoryMovementCorrectedEvent:
    with closing(connect()) as connection:
        try:
            connection.execute("BEGIN IMMEDIATE")
            original = connection.execute(
                "SELECT * FROM inventory_movements WHERE id = ?",
                (movement_id,),
            ).fetchone()
            if original is None:
                connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Inventory movement not found",
                )

            already_corrected = connection.execute(
                "SELECT 1 FROM inventory_movement_events WHERE original_movement_id = ?",
                (movement_id,),
            ).fetchone()
            if already_corrected is not None:
                connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Inventory movement has already been corrected",
                )

            compensation = compensating_movement(original, payload)
            current_stock = connection.execute(
                f"""
                SELECT COALESCE(SUM({MOVEMENT_STOCK_DELTA_SQL}), 0) AS current_stock
                FROM inventory_movements AS movement
                WHERE movement.item_id = ?
                """,
                (original["item_id"],),
            ).fetchone()["current_stock"]
            if current_stock + movement_delta(compensation) < 0:
                connection.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Correction would produce negative stock",
                )

            compensating_movement_id = str(uuid4())
            event_id = str(uuid4())
            occurred_at = utc_now()
            connection.execute(
                """
                INSERT INTO inventory_movements (
                    id, item_id, type, quantity, reason, recorded_at,
                    unit, direction, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    compensating_movement_id,
                    compensation.item_id,
                    compensation.type,
                    compensation.quantity,
                    compensation.reason,
                    compensation.recorded_at.isoformat(),
                    compensation.unit,
                    compensation.direction,
                    occurred_at,
                ),
            )
            connection.execute(
                """
                INSERT INTO inventory_movement_events (
                    id, event_type, original_movement_id,
                    compensating_movement_id, occurred_at
                ) VALUES (?, 'InventoryMovementCorrected', ?, ?, ?)
                """,
                (event_id, movement_id, compensating_movement_id, occurred_at),
            )
            connection.commit()
            compensating_row = connection.execute(
                "SELECT * FROM inventory_movements WHERE id = ?",
                (compensating_movement_id,),
            ).fetchone()
        except HTTPException:
            raise
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Movement correction could not be persisted",
            ) from error

    return InventoryMovementCorrectedEvent(
        id=event_id,
        original_movement_id=movement_id,
        compensating_movement=row_to_inventory_movement(compensating_row),
        occurred_at=occurred_at,
    )