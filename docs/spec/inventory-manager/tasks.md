# Inventory Manager Tasks

## Status

Stage 3: TASKS / Implementation through TASK-INV-006

This document defines the execution-level tasks required to satisfy the approved Inventory Manager Spec and Plan. These tasks are intentionally small, testable, and traceable to the approved requirements. TASK-INV-001 through TASK-INV-006 are implemented; later tasks remain pending.

---

## TASK-INV-001

### Objective

### Status

Completed

- AC-INV-002
- AC-INV-003
- AC-INV-019

### Verification

- Unit: invalid required fields, unsupported units, and negative reorder points are rejected; omitted values receive the defined defaults.
  Pending commit

### Dependencies

- None

### Commit

- `b85ecfb` (`task 1: completed`)

## TASK-INV-002

### Objective

Implement the inventory item lifecycle API.

### Status

Completed

### Changes

- Add create, list, retrieve, update, and remove/archive operations for inventory items.
- Restrict updates to allowed item fields and preserve movement history on update or removal.

### Acceptance Criteria

- AC-INV-001
- AC-INV-024
- AC-INV-025
- AC-INV-026

### Verification

- API: valid item lifecycle operations succeed; invalid updates do not alter movement history or derived stock; removal excludes the item from active operations without deleting history.

### Dependencies

- TASK-INV-001

### Commit

- `84e9f2d` (`TASK-INV-002`)

## TASK-INV-003

### Objective

Enforce the inventory-manager role for inventory operations.

### Status

Completed

### Changes

- Add the role dependency to item, movement, correction, and inventory-query operations.
- Reject unauthorized requests before any inventory mutation.

### Acceptance Criteria

- AC-INV-023

### Verification

- API: a request without `inventory-manager` is rejected and leaves inventory data unchanged.

### Dependencies

- TASK-INV-002

### Commit

- `288fa0a` (`TASK-INV-003`)

## TASK-INV-004

### Objective

Define shared inventory movement contracts and payload validation.

### Status

Completed

### Changes

- Add movement types, quantity, reason, timestamp, direction, and unit contracts in `packages/shared`.
- Validate movement type, positive quantity, reason, timestamp, adjustment direction, and item-unit consistency.

### Acceptance Criteria

- AC-INV-004
- AC-INV-006
- AC-INV-018
- AC-INV-027
- AC-INV-028

### Verification

- Unit: invalid movement payloads are rejected and valid payloads are accepted without requiring persistence or stock calculation.

### Dependencies

- TASK-INV-001

### Commit

- `350b47a` (`TASK-INV-004`)

## TASK-INV-005

### Objective

Register valid inventory movements and enforce negative-stock safety.

### Status

Completed

### Changes

- Add movement registration and persistence for incoming, outgoing, and adjustment movements.
- Reject unknown items and movements that would produce negative stock.

### Acceptance Criteria

- AC-INV-005
- AC-INV-020

### Verification

- Integration: unknown-item and negative-stock requests are rejected without creating a movement or changing derived stock.

### Dependencies

- TASK-INV-003
- TASK-INV-004

### Commit

- `48c3492` (`TASK-INV-005`)

## TASK-INV-006

### Objective

Implement current-stock derivation from movement history.

### Status

Completed

### Changes

- Calculate current stock from the complete movement history.
- Return `null` before the first movement and calculate from zero after the first movement.

### Acceptance Criteria

- AC-INV-007
- AC-INV-008
- AC-INV-009
- AC-INV-010
- AC-INV-012
- AC-INV-013
- AC-INV-021

### Verification

- Unit/integration: empty, incoming, outgoing, adjustment, and multi-movement histories produce the expected derived stock.

### Dependencies

- TASK-INV-005

### Commit

- Pending implementation

## TASK-INV-007

### Objective

Implement below-reorder-point evaluation and ordering.

### Changes

- Identify items strictly below a non-null reorder point.
- Exclude equal, above-threshold, and null-threshold items.
- Order results by descending stock deficit.

### Acceptance Criteria

- AC-INV-014
- AC-INV-015
- AC-INV-016

### Verification

- Integration: query results contain only below-threshold items and are ordered by `reorder_point - current_stock` descending.

### Dependencies

- TASK-INV-006

### Commit

- Pending implementation

## TASK-INV-008

### Objective

Prevent direct current-stock mutation.

### Changes

- Keep current stock read-only and derived.
- Reject API and domain operations that attempt to set or edit current stock.

### Acceptance Criteria

- AC-INV-011

### Verification

- API: direct current-stock mutation attempts are rejected and neither movement history nor derived stock changes.

### Dependencies

- TASK-INV-006

### Commit

- Pending implementation

## TASK-INV-009

### Objective

Implement immutable movement correction handling.

### Changes

- Preserve the original movement.
- Append a compensating movement and emit `InventoryMovementCorrected`.

### Acceptance Criteria

- AC-INV-022

### Verification

- Integration: correction retains the original movement, appends the compensating movement, and emits the correction event.

### Dependencies

- TASK-INV-005
- TASK-INV-006

### Commit

- Pending implementation

## TASK-INV-010

### Objective

Implement back-office inventory item lifecycle screens.

### Changes

- Add item create, list, detail, update, and remove/archive views.
- Show API validation errors for item lifecycle operations.

### Acceptance Criteria

- None owned; this task presents the behavior implemented by AC-INV-001, AC-INV-002, AC-INV-003, AC-INV-024, AC-INV-025, and AC-INV-026.

### Verification

- UI: users can complete each item lifecycle operation and see validation feedback without a current-stock input.

### Dependencies

- TASK-INV-002
- TASK-INV-008

### Commit

- Pending implementation

## TASK-INV-011

### Objective

Implement the back-office movement registration screen.

### Changes

- Add movement type, quantity, reason, timestamp, direction, and item-unit controls.
- Display movement validation and negative-stock errors returned by the API.

### Acceptance Criteria

- None owned; this task presents the behavior implemented by AC-INV-004, AC-INV-005, AC-INV-006, AC-INV-018, AC-INV-020, AC-INV-027, and AC-INV-028.

### Verification

- UI: users can submit a valid movement and receive field-level feedback for invalid or unsafe movement data.

### Dependencies

- TASK-INV-004
- TASK-INV-005

### Commit

- Pending implementation

## TASK-INV-012

### Objective

Expose derived stock and below-reorder-point signals in the back office.

### Changes

- Display current stock as read-only derived data.
- Show a visible replenishment alert for items below their reorder point.

### Acceptance Criteria

- AC-INV-029

### Verification

- UI: an item below its reorder point displays a visible alert, while current stock has no editable control.

### Dependencies

- TASK-INV-007
- TASK-INV-008

### Commit

- Pending implementation

## TASK-INV-013

### Objective

Run the final regression verification for the inventory module.

### Changes

- Execute the focused contract, API, integration, and UI checks owned by TASK-INV-001 through TASK-INV-012.
- Confirm no direct current-stock mutation path exists.

### Acceptance Criteria

- Release verification only; this task owns no additional business criterion.

### Verification

- Regression: all acceptance criteria AC-INV-001 through AC-INV-029 pass through their owning tasks.

### Dependencies

- TASK-INV-001
- TASK-INV-002
- TASK-INV-003
- TASK-INV-004
- TASK-INV-005
- TASK-INV-006
- TASK-INV-007
- TASK-INV-008
- TASK-INV-009
- TASK-INV-010
- TASK-INV-011
- TASK-INV-012

### Commit

- Pending implementation
