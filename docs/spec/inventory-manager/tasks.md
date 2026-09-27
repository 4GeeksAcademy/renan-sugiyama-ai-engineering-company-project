# Inventory Manager Tasks

## Status

Stage 3: TASKS

This document defines the execution-level tasks required to satisfy the approved Inventory Manager Spec and Plan. These tasks are intentionally small, testable, and traceable to the approved requirements. No implementation work is started here.

---

## TASK-INV-001

### Objective

Define the shared inventory item lifecycle contracts and validation rules required by the domain.

### Changes

- Add shared inventory item constants, enums, and contract types in `packages/shared`.
- Add validation helpers for identity, name, unit defaults, reorder points, supported units, and item update/remove rules.
- Add contract tests for successful and rejected item creation, update, list, and removal inputs.

### Acceptance Criteria

- AC-INV-001
- AC-INV-002
- AC-INV-003
- AC-INV-017
- AC-INV-019
- AC-INV-024
- AC-INV-025
- AC-INV-026

### Verification

- Unit: validation behavior for item creation and default values.
- Contract: request validation rejects missing identity, invalid name, negative reorder point, and unsupported unit values.

### Dependencies

- None

### Commit

- Pending implementation

---

## TASK-INV-002

### Objective

Define the inventory movement contracts and movement validation rules, including reason and timestamp requirements.

### Changes

- Add shared movement contract types and supported movement-type constants.
- Add validation helpers for movement quantity, movement reason, recorded timestamp, adjustment direction, item reference checks, and unit consistency.
- Add contract tests for valid and invalid movement payloads.

### Acceptance Criteria

- AC-INV-004
- AC-INV-005
- AC-INV-006
- AC-INV-018
- AC-INV-020
- AC-INV-027
- AC-INV-028

### Verification

- Unit: movement validation rejects unknown items, unsupported types, non-positive quantities, invalid adjustment direction, invalid units, and negative-stock outcomes.
- Contract: valid movement payloads are accepted when all domain rules are satisfied.

### Dependencies

- TASK-INV-001

### Commit

- Pending implementation

---

## TASK-INV-003

### Objective

Implement the inventory item lifecycle endpoints and enforcement of the inventory-manager role.

### Changes

- Add the item router and item lifecycle API logic in the centralized backend service.
- Validate required fields, default unit/reorder values, update rules, remove/archive behavior, and access control for inventory item operations.
- Add rejection handling for unauthorized and invalid item requests.

### Acceptance Criteria

- AC-INV-001
- AC-INV-002
- AC-INV-003
- AC-INV-019
- AC-INV-023
- AC-INV-024
- AC-INV-025
- AC-INV-026

### Verification

- API: create item succeeds for valid data and fails for invalid data.
- API: requests from users without `inventory-manager` role are rejected and do not create inventory data.

### Dependencies

- TASK-INV-001
- TASK-INV-002

### Commit

- Pending implementation

---

## TASK-INV-004

### Objective

Implement inventory movement registration, reason/timestamp checks, and stock-safety validation.

### Changes

- Add movement registration endpoint and persistence logic.
- Enforce supported movement types, reason requirement, timestamp requirement, and positive quantity rules.
- Block any movement that would reduce stock below zero.
- Ensure movement history is the only source of stock-affecting state.

### Acceptance Criteria

- AC-INV-004
- AC-INV-005
- AC-INV-006
- AC-INV-007
- AC-INV-008
- AC-INV-009
- AC-INV-020
- AC-INV-021
- AC-INV-027
- AC-INV-028

### Verification

- Integration: incoming, outgoing, and stock-adjustment movements update derived stock according to the movement history.
- API: invalid movement requests are rejected without changing the item’s resulting current stock.

### Dependencies

- TASK-INV-002
- TASK-INV-003

### Commit

- Pending implementation

---

## TASK-INV-005

### Objective

Implement current-stock and reorder-point calculation queries from movement history and expose the alert signal.

### Changes

- Add stock-derivation logic over the complete movement history for each inventory item.
- Add below-reorder-point query logic and ordering by `reorder_point - current_stock`.
- Exclude `null` reorder points and ensure equality is not treated as below threshold.
- Prevent any direct current-stock mutation path in API or domain logic.
- Expose a visible back-office alert when the stock is below the reorder point.

### Acceptance Criteria

- AC-INV-010
- AC-INV-011
- AC-INV-012
- AC-INV-013
- AC-INV-014
- AC-INV-015
- AC-INV-016
- AC-INV-029

### Verification

- Unit: stock derivation matches movement history for empty, single-movement, and multi-movement cases.
- Integration: below-reorder-point results include only valid items and are ordered by the largest deficit first.
- API: direct current-stock mutation attempts are rejected and no stock field is exposed as writable state.

### Dependencies

- TASK-INV-004

### Commit

- Pending implementation

---

## TASK-INV-006

### Objective

Implement immutability and correction handling for movement history.

### Changes

- Preserve original movements as immutable records.
- Add correction workflow that appends a compensating movement.
- Emit the `InventoryMovementCorrected` event when a movement is corrected.
- Ensure corrected history remains auditable and does not delete the original movement.

### Acceptance Criteria

- AC-INV-022

### Verification

- Integration: correcting a movement retains the original record and adds a compensating movement plus the correction event.
- API/contract: the response and event payload clearly represent the corrected movement history.

### Dependencies

- TASK-INV-004
- TASK-INV-005

### Commit

- Pending implementation

---

## TASK-INV-007

### Objective

Implement the operational back-office inventory views and user-facing validation for the item lifecycle and stock alerts.

### Changes

- Add item creation, list, detail, update, and removal screens for the back-office UI.
- Add movement registration screens with movement type, reason, and timestamp.
- Add below-reorder-point alerts and visible signal indicators.
- Ensure current stock is presented as derived data only, not as editable state.
- Include validation feedback consistent with API-level errors.

### Acceptance Criteria

- AC-INV-001
- AC-INV-004
- AC-INV-010
- AC-INV-011
- AC-INV-014
- AC-INV-016
- AC-INV-024
- AC-INV-025
- AC-INV-026
- AC-INV-027
- AC-INV-029

### Verification

- End-to-end: user can create items and movements and observe derived stock and reorder-point alerts.
- UI: no form control allows direct editing of current stock.

### Dependencies

- TASK-INV-003
- TASK-INV-004
- TASK-INV-005

### Commit

- Pending implementation

---

## TASK-INV-008

### Objective

Run acceptance-level verification across the inventory module.

### Changes

- Execute the focused contract, integration, and API tests covering the approved EARS acceptance criteria.
- Confirm the invariant that current stock derives exclusively from movements.
- Validate authorization failures, invalid movement rejection, and reorder-point behavior.

### Acceptance Criteria

- AC-INV-001 through AC-INV-023 as applicable to the release scope

### Verification

- API and integration verification against the approved acceptance criteria set.
- Regression check for no direct stock mutation path.

### Dependencies

- TASK-INV-001
- TASK-INV-002
- TASK-INV-003
- TASK-INV-004
- TASK-INV-005
- TASK-INV-006
- TASK-INV-007

### Commit

- Pending implementation

---

## Traceability summary

The task set is intentionally aligned with the approved requirements:

- Domain contracts, CRUD item lifecycle, and validation: TASK-INV-001, TASK-INV-002
- API and role enforcement for inventory items and movements: TASK-INV-003, TASK-INV-004
- Derived stock, reorder logic, and visible back-office signal: TASK-INV-005
- Correction event and immutability: TASK-INV-006
- UI and operational workflow for item lifecycle and stock alerts: TASK-INV-007
- Final acceptance verification: TASK-INV-008

This file remains a task definition only. No implementation code is modified here.
