from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

InventoryUnit = Literal["unit", "pack", "box", "ream", "roll", "liter", "kg"]
InventoryMovementType = Literal[
    "incoming_stock",
    "outgoing_stock",
    "stock_adjustment",
]
InventoryAdjustmentDirection = Literal["increase", "decrease"]


class InventoryItemCreate(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    unit: InventoryUnit = "unit"
    reorder_point: float | None = Field(default=None, ge=0)

    @field_validator("id", "name")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class InventoryItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    unit: InventoryUnit | None = None
    reorder_point: float | None = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def reject_blank_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value


class InventoryItemResponse(BaseModel):
    id: str
    name: str
    unit: InventoryUnit
    reorder_point: float | None
    current_stock: float | None
    created_at: str
    updated_at: str
    active: bool


class InventoryItemListResponse(BaseModel):
    items: list[InventoryItemResponse]


class InventoryMovementCreate(BaseModel):
    item_id: str = Field(min_length=1)
    type: InventoryMovementType
    quantity: float = Field(gt=0)
    reason: str = Field(min_length=1)
    recorded_at: datetime
    unit: InventoryUnit
    direction: InventoryAdjustmentDirection | None = None

    @field_validator("item_id", "reason")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def validate_adjustment_direction(self) -> "InventoryMovementCreate":
        if self.type == "stock_adjustment" and self.direction is None:
            raise ValueError("stock adjustment direction is required")
        if self.type != "stock_adjustment" and self.direction is not None:
            raise ValueError("direction is only valid for stock adjustments")
        return self


class InventoryMovementResponse(BaseModel):
    id: str
    item_id: str
    type: InventoryMovementType
    quantity: float
    reason: str
    recorded_at: datetime
    unit: InventoryUnit
    direction: InventoryAdjustmentDirection | None
    created_at: datetime


def validate_movement_unit(
    item_unit: InventoryUnit,
    movement_unit: InventoryUnit,
) -> None:
    if item_unit != movement_unit:
        raise ValueError("movement unit must match inventory item unit")
