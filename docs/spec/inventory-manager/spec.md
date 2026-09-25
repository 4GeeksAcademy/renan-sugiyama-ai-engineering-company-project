# Inventory Manager Specification

## Status

Stage 1: SPEC

This document defines what the inventory manager for Nexova Solutions must do. It does not define implementation architecture, files, APIs, persistence technology, or execution tasks.

## Scope

### Included

- Managing inventory items representing office materials used by Nexova Solutions.
- Registering inventory movements for those items.
- Supporting the movement concepts of incoming stock, outgoing stock, and stock adjustment.
- Providing the current stock of an inventory item as a value derived from its movement history.
- Identifying and listing inventory items whose current stock is below their reorder point.
- Validating inventory items and inventory movements according to the domain rules confirmed for this module.

### Excluded

- Procurement, supplier, purchase-order, or invoice management.
- Warehouse, location, lot, serial-number, or asset tracking.
- Direct editing or setting of current stock.
- Stock values maintained independently from inventory movements.
- Authentication and authorization policies other than the `inventory-manager` role are outside this feature.
- UI, API shape, persistence technology, deployment, and integration architecture.

## Domain concepts

No inventory domain model, schema, API, enum, or implementation currently exists in the repository. The terms below are therefore the terminology required by this business request, not terminology previously established by `CONTEXT.md` or existing source code.

### Canonical terminology and codes

The following English names are the canonical display terminology for this module. The corresponding `snake_case` codes are stable identifiers for APIs, persistence, filters, shared contracts, and tests. Display labels may be translated without changing these codes.

| Concept            | Official name      | Stable code          |
| ------------------ | ------------------ | -------------------- |
| Inventory item     | Inventory item     | `inventory_item`     |
| Inventory movement | Inventory movement | `inventory_movement` |
| Incoming stock     | Incoming stock     | `incoming_stock`     |
| Outgoing stock     | Outgoing stock     | `outgoing_stock`     |
| Stock adjustment   | Stock adjustment   | `stock_adjustment`   |

### Access role

The canonical role for this module is `inventory-manager`. Users with this role may perform inventory-manager operations. Users without this role may not perform inventory-manager operations.

### Inventory item

- **Purpose:** Represents an office material that Nexova needs to monitor.
- **Relevant attributes:** Identity and name are required. Unit of measure and reorder point are optional; omitted values use the defaults defined below.
- **Relationships:** An inventory item has zero or more inventory movements.
- **Constraints:** The item must have an identity and name. When provided, its reorder point must be zero or greater and must use the item's unit of measure.
- **Allowed values:** The canonical concept name and code are defined in the terminology table above. Supported units of measure are defined below. Item categories, statuses, and business identifiers are not established.

### Inventory movement

- **Purpose:** Records a stock-affecting event for one inventory item.
- **Relevant attributes:** The affected inventory item, movement type, and quantity are required. A stock adjustment also requires a direction. The movement inherits the inventory item's unit of measure.
- **Relationships:** Each movement belongs to exactly one inventory item.
- **Constraints:** A movement must refer to an existing inventory item, use a supported movement type, contain a strictly positive quantity, and use the item's unit of measure.
- **Allowed values:** The supported concepts are incoming stock (`incoming_stock`), outgoing stock (`outgoing_stock`), and stock adjustment (`stock_adjustment`).

### Movement types

- **Incoming stock:** Represents stock entering the inventory and increases current stock by the movement quantity.
- **Outgoing stock:** Represents stock leaving the inventory and decreases current stock by the movement quantity.
- **Stock adjustment:** Represents a correction to stock through a movement rather than through direct stock editing. It uses a strictly positive quantity and a direction of `increase` or `decrease`.

### Units of measure

Each inventory item shall use exactly one unit of measure. If no unit is provided, the system shall use `unit`. Its inventory movements, reorder point, and derived current stock shall use the same unit. Mixed units and automatic conversions are outside the scope of this module.

| Unit       | Stable code | Example               |
| ---------- | ----------- | --------------------- |
| Unit/piece | `unit`      | Pen or stapler        |
| Pack       | `pack`      | Pack of envelopes     |
| Box        | `box`       | Box of paper clips    |
| Ream       | `ream`      | Ream of printer paper |
| Roll       | `roll`      | Roll of labels        |
| Liter      | `liter`     | Cleaning liquid       |
| Kilogram   | `kg`        | Bulk material         |

### Current stock

- **Purpose:** Represents the quantity currently available for an inventory item.
- **Source:** Current stock is derived exclusively from the inventory item's inventory movements. If the item has no movements, the exposed current-stock value is `null`; once the first movement exists, calculation starts from zero and applies the movement history.
- **Constraint:** Current stock is not an independently writable domain value.

### Reorder point

- **Purpose:** Defines the stock threshold used to identify an inventory item that requires replenishment.
- **Constraint:** An item is below its reorder point when its derived current stock is strictly less than its reorder point.
- **Allowed values:** The reorder point is optional. When provided, it is zero or greater and uses the inventory item's supported unit of measure.

## Business rules and invariants

1. **Stock-from-movements invariant:** The current stock of an inventory item shall be calculated exclusively from its inventory movements.
2. Incoming stock increases derived current stock by its quantity.
3. Outgoing stock decreases derived current stock by its quantity.
4. Stock adjustments affect derived current stock through an inventory movement; they do not update a separate current-stock field.
5. Every stock-affecting change shall be represented by an inventory movement.
6. No operation in this module may directly set, edit, or mutate current stock.
7. An item is below its reorder point only when derived current stock is strictly less than the item's reorder point.
8. An item with derived current stock equal to its reorder point is not below the reorder point.
9. An item without movements exposes a `null` current-stock value. When the first movement is registered, stock calculation starts from zero and applies the movement history.
10. An inventory item, its reorder point, and all of its movements shall use one consistent supported unit of measure.
11. The system shall not convert quantities between units of measure.
12. Inventory movement quantities shall be strictly positive and may be fractional.
13. A reorder point shall be either `null` or zero or greater.
14. An outgoing movement or decreasing stock adjustment that would produce negative stock shall be rejected.
15. Registered movements shall remain immutable. A correction shall be represented by a compensating movement and an `InventoryMovementCorrected` domain event.
16. Inventory-manager operations shall require the `inventory-manager` role.

## Behavioral contracts

### Inventory item creation

The system shall accept a request to create an office-material inventory item when its identity and name are valid. Omitted unit of measure shall default to `unit`; omitted reorder point shall remain `null`. The created item shall be available for movement registration and stock queries.

The system shall reject an item creation request when identity or name is missing or invalid, or when an optional reorder point is negative. The rejection shall identify the validation failure and shall not create a partially valid item.

### Inventory movement registration

The system shall accept a movement when it identifies an existing inventory item, uses one of the supported movement concepts, contains a strictly positive quantity, and, for stock adjustment, contains direction `increase` or `decrease`.

The system shall reject a movement that references an unknown item, uses an unsupported movement type, contains a non-positive quantity, has an invalid adjustment direction, or would produce negative stock. A rejected movement shall not affect current stock.

### Current-stock query

The system shall return the current stock for an existing inventory item by deriving it from the complete applicable movement history.

The system shall not expose a command that directly sets or edits current stock. Any change in a returned current-stock value shall result from registering, correcting, or otherwise applying an inventory movement according to the approved movement rules.

The system shall preserve registered movements as immutable history. A correction shall append a compensating movement and emit `InventoryMovementCorrected`; it shall not edit or delete the original movement.

### Reorder-point query

The system shall identify an inventory item as below reorder point only when its derived current stock is strictly less than its reorder point.

The system shall support querying or listing inventory items whose reorder point is not `null` and whose derived current stock is below that reorder point. Results shall be ordered descending by `reorder_point - current_stock`, so the largest deficit appears first.

### Authorization

The system shall allow inventory-manager operations only for users with the `inventory-manager` role. The system shall reject requests from users without that role.

## Acceptance criteria (EARS)

### Item management

- **AC-INV-001:** The system shall create an inventory item for office material when its identity and name are valid.
- **AC-INV-002:** If an inventory item creation request contains a missing or invalid required attribute, then the system shall reject the request and shall not create the item.
- **AC-INV-003:** When an inventory item is created without a unit of measure or reorder point, the system shall default the unit to `unit` and preserve the reorder point as `null`.
- **AC-INV-019:** If an inventory item creation request contains a negative reorder point, then the system shall reject the request and shall not create the item.

### Movement management

- **AC-INV-004:** The system shall accept inventory movements whose movement type is incoming stock, outgoing stock, or stock adjustment.
- **AC-INV-005:** If an inventory movement references an inventory item that does not exist, then the system shall reject the movement and shall not change any current-stock result.
- **AC-INV-006:** If an inventory movement has an unsupported movement type, non-positive quantity, or invalid adjustment direction, then the system shall reject the movement and shall not change any current-stock result.
- **AC-INV-007:** When a valid incoming-stock movement is registered, the system shall include its quantity as an increase in the affected item's derived current stock.
- **AC-INV-008:** When a valid outgoing-stock movement is registered, the system shall include its quantity as a decrease in the affected item's derived current stock.
- **AC-INV-009:** When a valid stock-adjustment movement is registered, the system shall apply its positive quantity in its declared direction through movement history when deriving the affected item's current stock.
- **AC-INV-020:** If an outgoing movement or decreasing stock adjustment would produce negative stock, then the system shall reject the movement and shall not change the item's derived current stock.

### Stock invariant and current-stock evaluation

- **AC-INV-010:** The system shall calculate the current stock of an inventory item exclusively from that item's inventory movements.
- **AC-INV-011:** If a caller attempts to set or edit current stock directly, then the system shall reject the operation and shall leave the inventory movement history and derived current stock unchanged.
- **AC-INV-012:** When an inventory item has no registered movements, the system shall return a `null` current-stock value.
- **AC-INV-013:** When the current stock of an inventory item is queried, the system shall return a value consistent with the complete applicable movement history at query time.
- **AC-INV-021:** When the first movement for an inventory item is registered, the system shall calculate current stock from zero and the complete movement history.

### Reorder-point evaluation

- **AC-INV-014:** The system shall classify an inventory item as below reorder point when its reorder point is not `null` and its derived current stock is strictly less than its reorder point.
- **AC-INV-015:** If an inventory item's reorder point is `null` or its derived current stock is equal to or greater than its reorder point, then the system shall not classify the item as below reorder point.
- **AC-INV-016:** When a below-reorder-point query is performed, the system shall return only inventory items whose reorder point is not `null` and whose derived current stock is strictly less than their reorder points, ordered descending by `reorder_point - current_stock`.
- **AC-INV-017:** The system shall accept only the supported units of measure `unit`, `pack`, `box`, `ream`, `roll`, `liter`, and `kg` for an inventory item.
- **AC-INV-018:** If an inventory movement uses a unit of measure different from its inventory item, then the system shall reject the movement and shall not change the item's derived current stock.
- **AC-INV-022:** If a registered movement is corrected, then the system shall preserve the original movement, append a compensating movement, and emit `InventoryMovementCorrected`.
- **AC-INV-023:** If a request is made by a user without the `inventory-manager` role, then the system shall reject the request and shall not change inventory data.

## Open questions

No open questions remain for the decisions covered by this specification.
