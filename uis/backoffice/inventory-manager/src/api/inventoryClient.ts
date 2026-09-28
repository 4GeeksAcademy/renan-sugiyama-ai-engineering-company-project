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

export async function inventoryApi<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  headers.set("X-Inventory-User", USER_ID);

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const result = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(
      formatErrorDetail((result as { detail?: unknown } | null)?.detail) ||
        `Request failed (${response.status})`,
    );
  }
  return (response.status === 204 ? null : result) as T;
}
