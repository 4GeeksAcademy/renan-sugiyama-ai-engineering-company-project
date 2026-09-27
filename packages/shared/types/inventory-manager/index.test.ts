import {
  DEFAULT_INVENTORY_UNIT,
  INVENTORY_UNITS,
  isValidInventoryItemReorderPoint,
  isValidInventoryUnit,
  type CreateInventoryItemRequest,
  type InventoryItem,
} from "./index";

const inventoryItem: InventoryItem = {
  id: "inv-1",
  name: "Printer paper",
  unit: "ream",
  reorderPoint: 10,
  currentStock: 6,
  createdAt: "2026-09-25T12:00:00Z",
  updatedAt: "2026-09-25T12:30:00Z",
};

const inventoryCreationRequest: CreateInventoryItemRequest = {
  id: "inv-2",
  name: "Staples",
};

function assertContract(condition: boolean): void {
  if (!condition) {
    throw new Error("Shared inventory contract assertion failed");
  }
}

assertContract(inventoryItem.unit === "ream");
assertContract(DEFAULT_INVENTORY_UNIT === "unit");
assertContract(INVENTORY_UNITS.includes("pack"));
assertContract(isValidInventoryUnit("box"));
assertContract(!isValidInventoryUnit("invalid_unit"));
assertContract(isValidInventoryItemReorderPoint(null));
assertContract(isValidInventoryItemReorderPoint(0));
assertContract(!isValidInventoryItemReorderPoint(-1));
assertContract(inventoryCreationRequest.name === "Staples");
