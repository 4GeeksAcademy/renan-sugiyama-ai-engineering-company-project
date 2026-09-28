import type { BaseEntity, Id, IsoDateTime } from "../index";

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

export const INVENTORY_MOVEMENT_TYPES = [
  "incoming_stock",
  "outgoing_stock",
  "stock_adjustment",
] as const;

export type InventoryMovementType = (typeof INVENTORY_MOVEMENT_TYPES)[number];

export const INVENTORY_ADJUSTMENT_DIRECTIONS = [
  "increase",
  "decrease",
] as const;

export type InventoryAdjustmentDirection =
  (typeof INVENTORY_ADJUSTMENT_DIRECTIONS)[number];

export interface InventoryItem extends BaseEntity {
  name: string;
  unit: InventoryUnit;
  reorderPoint?: number | null;
  currentStock?: number | null;
}

export interface CreateInventoryItemRequest {
  id: Id;
  name: string;
  unit?: InventoryUnit;
  reorderPoint?: number | null;
}

export interface UpdateInventoryItemRequest {
  name?: string;
  unit?: InventoryUnit;
  reorderPoint?: number | null;
}

export interface InventoryMovement extends BaseEntity {
  itemId: Id;
  type: InventoryMovementType;
  quantity: number;
  reason: string;
  recordedAt: IsoDateTime;
  unit: InventoryUnit;
  direction?: InventoryAdjustmentDirection;
}

export interface CreateInventoryMovementRequest {
  itemId: Id;
  type: InventoryMovementType;
  quantity: number;
  reason: string;
  recordedAt: IsoDateTime;
  unit: InventoryUnit;
  direction?: InventoryAdjustmentDirection;
}

export function isValidInventoryUnit(value: unknown): value is InventoryUnit {
  return (
    typeof value === "string" &&
    INVENTORY_UNITS.includes(value as InventoryUnit)
  );
}

export function isValidInventoryMovementType(
  value: unknown,
): value is InventoryMovementType {
  return (
    typeof value === "string" &&
    INVENTORY_MOVEMENT_TYPES.includes(value as InventoryMovementType)
  );
}

export function isValidInventoryAdjustmentDirection(
  value: unknown,
): value is InventoryAdjustmentDirection {
  return (
    typeof value === "string" &&
    INVENTORY_ADJUSTMENT_DIRECTIONS.includes(
      value as InventoryAdjustmentDirection,
    )
  );
}

export function isValidInventoryMovementReason(
  value: unknown,
): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

export function isValidInventoryMovementTimestamp(
  value: unknown,
): value is IsoDateTime {
  return (
    typeof value === "string" &&
    value.trim().length > 0 &&
    !Number.isNaN(Date.parse(value))
  );
}

export function isValidInventoryMovementRequest(
  payload: Partial<CreateInventoryMovementRequest>,
  itemUnit?: InventoryUnit,
): payload is CreateInventoryMovementRequest {
  const isAdjustment = payload.type === "stock_adjustment";
  const hasValidDirection = isAdjustment
    ? isValidInventoryAdjustmentDirection(payload.direction)
    : payload.direction === undefined;

  return (
    isValidInventoryItemIdentity(payload.itemId) &&
    isValidInventoryMovementType(payload.type) &&
    typeof payload.quantity === "number" &&
    Number.isFinite(payload.quantity) &&
    payload.quantity > 0 &&
    isValidInventoryMovementReason(payload.reason) &&
    isValidInventoryMovementTimestamp(payload.recordedAt) &&
    isValidInventoryUnit(payload.unit) &&
    (itemUnit === undefined || payload.unit === itemUnit) &&
    hasValidDirection
  );
}

export function isValidInventoryItemIdentity(value: unknown): value is Id {
  return typeof value === "string" && value.trim().length > 0;
}

export function isValidInventoryItemName(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

export function isValidInventoryItemCreationRequest(
  payload: Partial<CreateInventoryItemRequest>,
): payload is CreateInventoryItemRequest {
  return (
    isValidInventoryItemIdentity(payload.id) &&
    isValidInventoryItemName(payload.name) &&
    (payload.unit === undefined || isValidInventoryUnit(payload.unit)) &&
    isValidInventoryItemReorderPoint(payload.reorderPoint)
  );
}

export function normalizeInventoryItemUnit(
  value?: InventoryUnit | null,
): InventoryUnit {
  return value && isValidInventoryUnit(value) ? value : DEFAULT_INVENTORY_UNIT;
}

export function normalizeInventoryItemCreationRequest(
  payload: Partial<CreateInventoryItemRequest>,
): CreateInventoryItemRequest | null {
  if (!isValidInventoryItemCreationRequest(payload)) {
    return null;
  }

  return {
    id: payload.id,
    name: payload.name,
    unit: normalizeInventoryItemUnit(payload.unit),
    reorderPoint: payload.reorderPoint ?? null,
  };
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
