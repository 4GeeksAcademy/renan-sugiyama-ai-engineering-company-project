import type { BaseEntity, Id } from "../index";

export const DEFAULT_INVENTORY_UNIT = "unit" as const;

export const INVENTORY_UNITS = [
  "unit",
  "pack",
  "box",
  "ream",
  "roll",
  "liter",
  "kg",
] as const;

export type InventoryUnit = (typeof INVENTORY_UNITS)[number];

export interface InventoryItem extends BaseEntity {
  name: string;
  unit: InventoryUnit;
  reorderPoint?: number | null;
  currentStock?: number | null;
}

export interface CreateInventoryItemRequest {
  id?: Id;
  name: string;
  unit?: InventoryUnit;
  reorderPoint?: number | null;
}

export interface UpdateInventoryItemRequest {
  name?: string;
  unit?: InventoryUnit;
  reorderPoint?: number | null;
}

export function isValidInventoryUnit(value: unknown): value is InventoryUnit {
  return (
    typeof value === "string" &&
    INVENTORY_UNITS.includes(value as InventoryUnit)
  );
}

export function isValidInventoryItemIdentity(value: unknown): value is Id {
  return typeof value === "string" && value.trim().length > 0;
}

export function isValidInventoryItemName(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

export function normalizeInventoryItemUnit(
  value?: InventoryUnit | null,
): InventoryUnit {
  return value && isValidInventoryUnit(value) ? value : DEFAULT_INVENTORY_UNIT;
}

export function isValidInventoryItemReorderPoint(
  value: number | null | undefined,
): boolean {
  return value == null || (Number.isFinite(value) && value >= 0);
}

export function isValidInventoryItemLifecycleUpdate(
  payload: Partial<UpdateInventoryItemRequest>,
): boolean {
  if (payload.name !== undefined && !isValidInventoryItemName(payload.name)) {
    return false;
  }

  if (payload.unit !== undefined && !isValidInventoryUnit(payload.unit)) {
    return false;
  }

  if (
    payload.reorderPoint !== undefined &&
    !isValidInventoryItemReorderPoint(payload.reorderPoint)
  ) {
    return false;
  }

  return true;
}

export function canRemoveInventoryItem(
  item: Pick<InventoryItem, "reorderPoint" | "currentStock">,
): boolean {
  return item.currentStock == null || item.currentStock >= 0;
}
