import type { InventoryItem } from "../api/inventoryClient";

export function formatQuantity(value: number | null, unit: string): string {
  return value === null
    ? "No movements"
    : `${new Intl.NumberFormat(undefined, { maximumFractionDigits: 3 }).format(value)} ${unit}`;
}

export function isBelowReorderPoint(item: InventoryItem): boolean {
  return (
    item.current_stock !== null &&
    item.reorder_point !== null &&
    item.current_stock < item.reorder_point
  );
}

export function ItemError({ message }: { message: string }) {
  return (
    <p className="inventory-error" role="alert">
      {message}
    </p>
  );
}
