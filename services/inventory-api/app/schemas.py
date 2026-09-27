from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

InventoryUnit = Literal["unit", "pack", "box", "ream", "roll", "liter", "kg"]


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
