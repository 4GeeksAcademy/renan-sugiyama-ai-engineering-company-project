# Inventory Manager Implementation Plan

## Status

Stage 2: PLAN

## 1. Purpose

Implement the inventory-manager module so Nexova Solutions can create inventory items, register valid inventory movements, calculate current stock exclusively from movement history, and identify items below reorder point. This plan defines the architecture and design choices required to satisfy the approved inventory specification without introducing direct current-stock mutation paths.

## 2. Business objective

The module must support:

- inventory item creation and validation;
- inventory movement registration for incoming stock, outgoing stock, and stock adjustment;
- current-stock derivation from movement history;
- reorder-point evaluation and below-threshold listing;
- authorization checks based on the `inventory-manager` role;
- validation and rejection of invalid or negative-stock operations.

## 3. Repository fit and architecture

This solution should follow the repository’s established layer boundaries:

- `packages/shared` for reusable inventory contracts, enums, validation helpers, and typed request/response schemas.
- `services/` for the centralized backend service, mirroring the existing FastAPI pattern used by the incident API.
- `uis/backoffice` for any operational inventory views, filtering, and form interactions that surface inventory data.
- `docs/spec/inventory-manager` as the source of truth for business and acceptance requirements.

The backend implementation will be organized to match the existing service conventions already used in the repo, especially the pattern under `services/incident-api/app` with `main.py`, `schemas.py`, `db.py`, and router modules.

## 4. Scope of the plan

### In scope

- Inventory item lifecycle: creation, retrieval, listing, updating, and removal with the defined item fields.
- Inventory item domain model and validation.
- Supported inventory movement types, movement reason, movement timestamp, and unit-of-measure rules.
- Derived current-stock logic from movement history.
- Reorder-point threshold evaluation and below-reorder-point queries.
- Visible back-office signal when an item is below its reorder point.
- API and persistence validation rules for item lifecycle management, movement registration, and stock queries.
- Authorization and role enforcement for inventory-manager actions.
- Shared typed contracts used by backend and UI.

### Out of scope

- Procurement, supplier, purchase-order, or invoice workflows.
- Warehouse locations, lot numbers, serial tracking, or asset inventory hierarchies.
- Direct writes to current stock outside of movement-driven behavior.
- Unit conversion, multi-location tracking, or other quantity normalization rules.
- UI/UX design beyond the minimal operational back-office screens needed to validate the business flow.

## 5. Domain model and data design

### Inventory item

The model will include:

- unique item identity;
- name;
- unit of measure with default `unit` when omitted;
- optional reorder point;
- lifecycle metadata needed for item creation, listing, updating, and removal;
- relationship to its movement history.

This supports AC-INV-001, AC-INV-002, AC-INV-003, AC-INV-017, AC-INV-019, AC-INV-024, AC-INV-025, and AC-INV-026.

### Inventory movement

The model will include:

- inventory item reference;
- movement type;
- quantity;
- reason;
- recorded timestamp;
- direction for stock adjustments;
- immutable record semantics.

The movement types are the canonical domain values already defined by the specification: `incoming_stock`, `outgoing_stock`, and `stock_adjustment`.

This supports AC-INV-004, AC-INV-005, AC-INV-006, AC-INV-018, AC-INV-020, AC-INV-027, and AC-INV-028.

### Stock and reorder-point logic

The model will deliberately avoid a writable current-stock field. Instead, stock will be computed dynamically from the inventory item’s movement history using the domain rules defined in the spec. This includes:

- no direct current-stock setter;
- no direct stock mutation API or form field;
- negative-stock rejection when valid movement rules would breach zero;
- below-reorder-point evaluation based on strict comparison with current stock.

This supports AC-INV-010, AC-INV-011, AC-INV-012, AC-INV-013, AC-INV-014, AC-INV-015, AC-INV-016, AC-INV-021, and AC-INV-022.

## 6. Shared contracts and validation

### Shared package changes

The shared layer will define canonical inventory constants and contracts, including:

- item creation request and item response models;
- movement request and movement response models;
- movement type enum-like values;
- unit-of-measure values and validation helpers;
- reorder-point and current-stock query shapes;
- inventory list and below-reorder-point response models;
- API error payloads for validation and authorization failures.

The shared package should also include validation helpers for:

- required item identity and name;
- non-negative reorder-point checks;
- supported movement types;
- positive quantity validation;
- stock-adjustment direction validation;
- allowed units of measure;
- movement/item unit consistency checks.

This supports AC-INV-001, AC-INV-002, AC-INV-003, AC-INV-004, AC-INV-006, AC-INV-017, AC-INV-018, and AC-INV-019.

## 7. Backend service design

### Service structure

The backend will follow the centralized FastAPI pattern used elsewhere in the repo. The likely service layout is:

- `services/inventory-api/app/main.py`
- `services/inventory-api/app/schemas.py`
- `services/inventory-api/app/db.py`
- `services/inventory-api/app/dependencies.py`
- `services/inventory-api/app/routers/inventory_items.py`
- `services/inventory-api/app/routers/inventory_movements.py`
- `services/inventory-api/app/routers/summary.py`
- `services/inventory-api/app/routers/health.py`
- `services/inventory-api/migrations/` for schema evolution

### API behavior

The service will expose the operations required by the specification without creating a direct stock-update endpoint:

- create inventory item;
- list and fetch items;
- update inventory item metadata within the allowed fields;
- remove or archive an inventory item from active operations;
- register movement with reason and timestamp;
- list/retrieve movement history for an item;
- query current stock;
- query below-reorder-point items;
- reject invalid movement, invalid item lifecycle operations, or authorization requests.

The API must enforce that any stock value is derived from movement history, not persisted as a separate mutable field. The current-stock API is read-only and computed from movement events at query time.

This supports AC-INV-005, AC-INV-007, AC-INV-008, AC-INV-009, AC-INV-010, AC-INV-011, AC-INV-012, AC-INV-013, AC-INV-014, AC-INV-015, AC-INV-016, AC-INV-020, AC-INV-021, AC-INV-022, and AC-INV-023.

## 8. Persistence and movement history

The persistence layer will store:

- inventory items as persistent records;
- inventory movements as immutable event history;
- derived stock queries computed from the full movement set for a given item.

Implementation decisions will include:

- a one-to-many relationship from item to movements;
- strict validation at persistence time for movement type, quantity, unit consistency, and stock safety;
- a correction pattern that preserves the original movement and appends a compensating movement rather than altering historic records;
- audit or event metadata for corrected movements, consistent with the specification’s `InventoryMovementCorrected` event requirement.

This supports AC-INV-020 and AC-INV-022.

## 9. Authorization and role checks

The inventory module will enforce the canonical role `inventory-manager` for all inventory-management operations.

The backend will reject requests from users lacking the role without mutating inventory data. This includes item creation, movement registration, correction handling, and reorder-point queries that create or modify inventory state.

This supports AC-INV-023.

## 10. Reorder-point evaluation

The module will evaluate reorder-point status using the rule:

- an item is below its reorder point when its derived current stock is strictly less than the reorder point;
- equal-to-threshold items are not considered below threshold;
- `null` reorder points are excluded from alert lists.

The below-threshold query will be ordered descending by `reorder_point - current_stock` so the largest stock deficit appears first. The back-office UI will surface an explicit visible signal for these items so operators can act before stock runs out.

This supports AC-INV-014, AC-INV-015, AC-INV-016, and AC-INV-029.

## 11. UI and operational views

The back-office UI will contain the minimal operational screens needed to validate the domain flow:

- create inventory item form;
- list and detail view for inventory items;
- update inventory item form using the defined item fields;
- remove or archive action for an inactive item;
- movement registration form with supported movement types, reason, and timestamp;
- stock and reorder-point summaries;
- visible below-reorder-point alert list;
- validation feedback for invalid entities and movements.

The UI must not expose a direct current-stock editing control. Any stock changes visible to users must be a consequence of movement registration and derived recalculation.

This supports AC-INV-001, AC-INV-004, AC-INV-010, AC-INV-011, AC-INV-014, AC-INV-016, AC-INV-024, AC-INV-025, AC-INV-026, AC-INV-027, and AC-INV-029.

## 12. Test strategy

The implementation should validate the approved specification through layered tests, with emphasis on real behavior rather than mock-only checks.

### Unit tests

- item validation logic;
- movement validation logic;
- stock derivation from movement sequences;
- reorder-point comparison rules;
- negative-stock prevention logic.

### Integration tests

- create item + movement flow;
- invalid item rejection;
- invalid movement rejection;
- below-reorder-point query results;
- event/correction semantics.

### API tests

- create item endpoint validation;
- movement registration endpoint validation;
- stock query contract and error behavior;
- authorization failure responses.

This plan is intentionally aligned with the approval gate in the spec, and the test suite will be derived from the acceptance criteria above.

## 13. Acceptance-criteria traceability

The plan is structured to satisfy the spec’s EARS acceptance criteria as follows:

- Item lifecycle and defaults: AC-INV-001, AC-INV-002, AC-INV-003, AC-INV-019, AC-INV-024, AC-INV-025, AC-INV-026
- Movement validation and supported types: AC-INV-004, AC-INV-005, AC-INV-006, AC-INV-017, AC-INV-018, AC-INV-020, AC-INV-027, AC-INV-028
- Stock derivation and invariant: AC-INV-010, AC-INV-011, AC-INV-012, AC-INV-013, AC-INV-021
- Reorder-point behavior and visibility: AC-INV-014, AC-INV-015, AC-INV-016, AC-INV-029
- Correction and authorization: AC-INV-022, AC-INV-023

## 14. Delivery sequence

1. Confirm shared contracts and inventory domain constants.
2. Implement item and movement validation in the backend.
3. Add movement-history storage and derived stock calculation.
4. Implement reorder-point query and alert ordering logic.
5. Enforce inventory-manager role checks and reject invalid operations.
6. Add UI and contract validation for the main operational flows.
7. Run acceptance-focused verification against the spec’s EARS criteria.

## 15. Implementation gate

Implementation will begin only after this plan is explicitly approved and the next stage is authorized. This plan remains limited to architecture and design; it does not create tasks or begin code implementation.
