import { track } from "@nexova/telemetry";
import { InventoryApiError } from "./inventoryClient";
import type {
  InventoryItem,
  InventoryMovement,
  InventoryMovementCreate,
} from "./inventoryClient";

const round = (value: number) => Math.round(value * 1e6) / 1e6;

function stockDelta(payload: InventoryMovementCreate): number {
  if (payload.type === "incoming_stock") return payload.quantity;
  if (payload.type === "outgoing_stock") return -payload.quantity;
  return payload.direction === "decrease"
    ? -payload.quantity
    : payload.quantity;
}

export function trackMovementRecorded(
  item: InventoryItem,
  payload: InventoryMovementCreate,
  movement: InventoryMovement,
): void {
  const stockBefore = item.current_stock;
  const stockAfter = Math.max(
    0,
    round((stockBefore ?? 0) + stockDelta(payload)),
  );

  track("stock_movement_recorded", {
    movementId: movement.id,
    itemId: movement.item.id,
    movementType: movement.type,
    quantity: movement.quantity,
    unit: movement.unit,
    stockBefore,
    stockAfter,
    value: stockDelta(payload),
  });

  const reorderPoint = item.reorder_point;
  if (
    reorderPoint !== null &&
    stockBefore !== null &&
    stockBefore >= reorderPoint &&
    stockAfter < reorderPoint
  ) {
    track("stock_threshold_triggered", {
      itemId: movement.item.id,
      stockBefore,
      stockAfter,
      reorderPoint,
      crossing: "below",
    });
  }
}

const VALIDATION_CODES: Record<number, string> = {
  400: "bad_request",
  404: "not_found",
  409: "conflict",
  422: "invalid_field",
};

const VALIDATION_MESSAGES: Record<string, string> = {
  bad_request: "Stock movement request was invalid.",
  not_found: "Stock movement item was not found.",
  conflict: "Stock movement conflicts with available stock.",
  invalid_field: "Stock movement contains an invalid field.",
};

export function trackMovementRejected(
  item: InventoryItem | undefined,
  payload: InventoryMovementCreate,
  error: unknown,
): void {
  if (!(error instanceof InventoryApiError)) return;

  if (
    error.status === 409 &&
    payload.type !== "incoming_stock" &&
    error.fieldErrors.quantity &&
    item
  ) {
    track("outbound_stock_blocked", {
      itemId: item.id,
      availableStock: item.current_stock ?? 0,
      requestedQuantity: payload.quantity,
      unit: item.unit,
      httpStatus: 409,
      value: payload.quantity,
      message: "Outbound stock movement exceeded available stock.",
    });
    return;
  }

  const code = VALIDATION_CODES[error.status];
  if (!code) return;
  const field = Object.keys(error.fieldErrors)[0];
  track("stock_movement_validation_failed", {
    route: "/inventory/movements",
    validationCode: code,
    field: field && /^[a-zA-Z][a-zA-Z0-9_]*$/.test(field) ? field : null,
    httpStatus: error.status,
    value: payload.quantity,
    message: VALIDATION_MESSAGES[code],
  });
}
