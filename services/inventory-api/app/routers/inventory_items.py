from __future__ import annotations

from contextlib import closing

from fastapi import APIRouter, Depends, HTTPException, status

from app.db import INVENTORY_ITEM_SELECT, connect, row_to_inventory_item, utc_now
from app.dependencies import inventory_manager_user
from app.schemas import (
    InventoryItemCreate,
    InventoryItemListResponse,
    InventoryItemResponse,
    InventoryItemUpdate,
)

router = APIRouter(
    prefix="/inventory/items",
    tags=["inventory-items"],
    dependencies=[Depends(inventory_manager_user)],
)


@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(payload: InventoryItemCreate) -> InventoryItemResponse:
    now = utc_now()
    with closing(connect()) as connection:
        try:
            connection.execute(
                """
                INSERT INTO inventory_items (
                    id, name, unit, reorder_point, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.id,
                    payload.name,
                    payload.unit,
                    payload.reorder_point,
                    now,
                    now,
                ),
            )
            connection.commit()
        except Exception as error:
            if "UNIQUE constraint failed" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Inventory item already exists",
                ) from error
            raise
        row = connection.execute(
            INVENTORY_ITEM_SELECT + " WHERE id = ? AND active = 1",
            (payload.id,),
        ).fetchone()
    return row_to_inventory_item(row)


@router.get("", response_model=InventoryItemListResponse)
def list_items() -> InventoryItemListResponse:
    with closing(connect()) as connection:
        rows = connection.execute(
            INVENTORY_ITEM_SELECT + " WHERE active = 1 ORDER BY name ASC, id ASC"
        ).fetchall()
    return InventoryItemListResponse(items=[row_to_inventory_item(row) for row in rows])


@router.get("/below-reorder-point", response_model=InventoryItemListResponse)
def list_items_below_reorder_point() -> InventoryItemListResponse:
    with closing(connect()) as connection:
        rows = connection.execute(
            f"""
            SELECT *
            FROM ({INVENTORY_ITEM_SELECT}) AS inventory_item
            WHERE inventory_item.active = 1
              AND inventory_item.reorder_point IS NOT NULL
              AND inventory_item.current_stock IS NOT NULL
              AND inventory_item.current_stock < inventory_item.reorder_point
            ORDER BY inventory_item.reorder_point - inventory_item.current_stock DESC,
                     inventory_item.name ASC,
                     inventory_item.id ASC
            """
        ).fetchall()
    return InventoryItemListResponse(items=[row_to_inventory_item(row) for row in rows])


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_item(item_id: str) -> InventoryItemResponse:
    with closing(connect()) as connection:
        row = connection.execute(
            INVENTORY_ITEM_SELECT + " WHERE id = ? AND active = 1",
            (item_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return row_to_inventory_item(row)


@router.patch("/{item_id}", response_model=InventoryItemResponse)
def update_item(item_id: str, payload: InventoryItemUpdate) -> InventoryItemResponse:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one item field is required",
        )

    assignments = ", ".join(f"{field} = ?" for field in changes)
    values = list(changes.values()) + [utc_now(), item_id]
    with closing(connect()) as connection:
        cursor = connection.execute(
            f"UPDATE inventory_items SET {assignments}, updated_at = ? "
            "WHERE id = ? AND active = 1",
            values,
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )
        connection.commit()
        row = connection.execute(
            INVENTORY_ITEM_SELECT + " WHERE id = ? AND active = 1",
            (item_id,),
        ).fetchone()
    return row_to_inventory_item(row)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(item_id: str) -> None:
    with closing(connect()) as connection:
        cursor = connection.execute(
            "UPDATE inventory_items SET active = 0, archived_at = ?, updated_at = ? "
            "WHERE id = ? AND active = 1",
            (utc_now(), utc_now(), item_id),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )
        connection.commit()
