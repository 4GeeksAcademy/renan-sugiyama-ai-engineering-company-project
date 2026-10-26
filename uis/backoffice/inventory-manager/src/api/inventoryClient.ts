import { track } from "@nexova/telemetry";
import {
  getTelemetryContext,
  setTelemetryContext,
} from "@nexova/telemetry/context";

const API_BASE = window.INVENTORY_API_URL || "http://localhost:8001";
const USER_ID = window.INVENTORY_USER_ID || "local-user";

export type InventoryUnit =
  | "unit"
  | "pack"
  | "box"
  | "ream"
  | "roll"
  | "liter"
  | "kg";

export type InventoryItem = {
  id: string;
  name: string;
  unit: InventoryUnit;
  reorder_point: number | null;
  current_stock: number | null;
  created_at: string;
  updated_at: string;
  active: boolean;
};

export type InventoryItemList = { items: InventoryItem[] };

export type InventoryItemCreate = {
  id: string;
  name: string;
  unit: InventoryUnit;
  reorder_point: number | null;
};

export type InventoryItemUpdate = Omit<InventoryItemCreate, "id">;

export type InventoryMovementType =
  | "incoming_stock"
  | "outgoing_stock"
  | "stock_adjustment";

export type InventoryItemReference = Pick<
  InventoryItem,
  "id" | "name" | "unit"
>;

export type InventoryMovement = {
  id: string;
  item: InventoryItemReference;
  type: InventoryMovementType;
  quantity: number;
  reason: string;
  recorded_at: string;
  unit: InventoryUnit;
  direction: "increase" | "decrease" | null;
  created_at: string;
};

export type InventoryMovementCreate = {
  item_id: string;
  type: InventoryMovementType;
  quantity: number;
  reason: string;
  recorded_at: string;
  unit: InventoryUnit;
  direction: "increase" | "decrease" | null;
};

export class InventoryApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly fieldErrors: Record<string, string>,
  ) {
    super(message);
    this.name = "InventoryApiError";
  }
}

function formatErrorDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((entry) => {
        if (!entry || typeof entry !== "object") return String(entry);
        const error = entry as { loc?: unknown[]; msg?: string };
        const field = error.loc?.at(-1);
        return `${field ? `${String(field)}: ` : ""}${error.msg || "Invalid value"}`;
      })
      .join("; ");
  }
  return "The inventory request could not be completed.";
}

function routeTemplate(path: string): string {
  return path
    .split("?")[0]
    .replace(
      /^(\/inventory\/items)\/(?!below-reorder-point$)[^/]+/,
      "$1/{item_id}",
    )
    .replace(/^(\/inventory\/movements)\/[^/]+/, "$1/{movement_id}");
}

const ERROR_CODES: Record<number, string> = {
  400: "bad_request",
  401: "unauthorized",
  403: "forbidden",
  404: "not_found",
  409: "conflict",
  422: "validation_error",
};

function trackResponse(
  path: string,
  method: string,
  status: number,
  durationMs: number,
): void {
  const route = routeTemplate(path);
  track("api_latency_recorded", {
    routeTemplate: route,
    method,
    httpStatus: status,
    durationMs: Math.round(durationMs),
  });
  if (status < 400) return;

  track("api_request_failed", {
    routeTemplate: route,
    method,
    httpStatus: status,
    errorCode:
      ERROR_CODES[status] ?? (status >= 500 ? "server_error" : "client_error"),
    retryable: status >= 500 || status === 429,
  });
  if (status === 401 || status === 403) {
    track("user_authentication_denied", {
      reason: status === 401 ? "missing_identity" : "unknown_user",
      route,
      httpStatus: status,
    });
  }
}

export async function inventoryApi<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  headers.set("X-Inventory-User", USER_ID);

  const context = getTelemetryContext();
  if (context) {
    setTelemetryContext({ ...context, requestId: crypto.randomUUID() });
  }
  const startedAt = performance.now();
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  trackResponse(
    path,
    (options.method || "GET").toUpperCase(),
    response.status,
    performance.now() - startedAt,
  );
  const result = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = (result as { detail?: unknown } | null)?.detail;
    const fieldErrors: Record<string, string> = {};
    if (Array.isArray(detail)) {
      for (const entry of detail) {
        if (!entry || typeof entry !== "object") continue;
        const issue = entry as { loc?: unknown[]; msg?: string };
        const field = issue.loc?.at(-1);
        if (field) {
          const key = String(field);
          fieldErrors[key] = fieldErrors[key]
            ? `${fieldErrors[key]}; ${issue.msg || "Invalid value"}`
            : issue.msg || "Invalid value";
        }
      }
    } else if (typeof detail === "string") {
      const message = detail.toLowerCase();
      if (message.includes("negative stock") || message.includes("quantity")) {
        fieldErrors.quantity = detail;
      } else if (message.includes("unit")) {
        fieldErrors.unit = detail;
      } else if (message.includes("item")) {
        fieldErrors.item_id = detail;
      }
    }
    throw new InventoryApiError(
      formatErrorDetail(detail) || `Request failed (${response.status})`,
      response.status,
      fieldErrors,
    );
  }
  return (response.status === 204 ? null : result) as T;
}
