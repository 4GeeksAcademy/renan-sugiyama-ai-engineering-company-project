# FastAPI Endpoint Inventory

This inventory covers the explicitly declared API routes under `services/`. The three applications expose 20 declared endpoints in total.

For each endpoint, the response behavior distinguishes an explicit `response_model` from a schema inferred from the handler's return annotation. The return description reflects the handler value before FastAPI serializes it.

### Serialization Status

- ✅ **Already serialized:** An explicit `response_model` provides an appropriate response contract. The inventory `204 No Content` route is an intentional exception: there is no response body to model.
- ⚠️ **Partially serialized:** A typed response is inferred rather than explicitly modeled, or a response model is broader or less constrained than the current UI-facing contract.
- ❌ **Not serialized:** The endpoint returns a generic dict without a useful field-level response schema.

The incident comparison uses the current local types in `uis/backoffice/incident-manager/src/types/index.ts`; the inventory comparison uses the types in `uis/backoffice/inventory-manager/src/api/inventoryClient.ts`.

## Incident API

Route definitions: [`services/incident-api/app/routers/`](../services/incident-api/app/routers/)

| Status                | Method  | Route                                 | Purpose                                                                                   | Response behavior                                                                                          |
| --------------------- | ------- | ------------------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| ✅ Already serialized | `GET`   | `/health`                             | Return the service health status.                                                         | Explicit `response_model=HealthResponse`.                                                                  |
| ✅ Already serialized | `GET`   | `/catalogs`                           | Return the allowed incident channels, types, severities, statuses, and responsible areas. | Explicit `response_model=IncidentCatalogsResponse` with fixed fields and literal value types.              |
| ✅ Already serialized | `POST`  | `/incidents`                          | Create an incident.                                                                       | Explicit `response_model=IncidentResponse` restricted to fields in the current UI incident type.           |
| ✅ Already serialized | `GET`   | `/incidents`                          | List incidents with search, filtering, sorting, and pagination.                           | Explicit `response_model=IncidentListResponse` with typed incident items and the client pagination fields. |
| ✅ Already serialized | `GET`   | `/incidents/{incident_id}`            | Retrieve an incident and its audit history.                                               | Explicit `response_model=IncidentDetailResponse` with client-facing incident and audit fields.             |
| ✅ Already serialized | `PATCH` | `/incidents/{incident_id}`            | Update incident fields.                                                                   | Explicit `response_model=IncidentResponse` restricted to fields in the current UI incident type.           |
| ✅ Already serialized | `POST`  | `/incidents/{incident_id}/assignment` | Reassign an incident and record the change.                                               | Explicit `response_model=IncidentResponse` restricted to fields in the current UI incident type.           |
| ✅ Already serialized | `POST`  | `/incidents/{incident_id}/status`     | Change incident status and record the change.                                             | Explicit `response_model=IncidentResponse` restricted to fields in the current UI incident type.           |
| ✅ Already serialized | `GET`   | `/incidents/{incident_id}/history`    | Retrieve an incident's audit events.                                                      | Explicit `response_model=list[AuditEventResponse]` matching the current UI audit fields.                   |
| ✅ Already serialized | `GET`   | `/summary`                            | Return open-incident counts and SLA/backlog metrics.                                      | Explicit `response_model=SummaryResponse` constraining severity keys.                                      |

Routes other than `/health` require the back-office user dependency.

## Inventory API

Route definitions: [`services/inventory-api/app/routers/inventory_items.py`](../services/inventory-api/app/routers/inventory_items.py) and [`services/inventory-api/app/routers/inventory_movements.py`](../services/inventory-api/app/routers/inventory_movements.py)

| Status                | Method   | Route                                           | Purpose                                                                                               | Response behavior                                                                                                                                |
| --------------------- | -------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| ✅ Already serialized | `POST`   | `/inventory/items`                              | Create an inventory item.                                                                             | Explicit `response_model=InventoryItemResponse`; typed schema matches the inventory client item shape.                                           |
| ✅ Already serialized | `GET`    | `/inventory/items`                              | List active inventory items.                                                                          | Explicit `response_model=InventoryItemListResponse`; typed list schema matches the inventory client list shape.                                  |
| ✅ Already serialized | `GET`    | `/inventory/items/below-reorder-point`          | List active items below their reorder point.                                                          | Explicit `response_model=InventoryItemListResponse`; typed list schema matches the inventory client list shape.                                  |
| ✅ Already serialized | `GET`    | `/inventory/items/{item_id}`                    | Retrieve an inventory item.                                                                           | Explicit `response_model=InventoryItemResponse`; typed schema matches the inventory client item shape.                                           |
| ✅ Already serialized | `PATCH`  | `/inventory/items/{item_id}`                    | Update an inventory item.                                                                             | Explicit `response_model=InventoryItemResponse`; typed schema matches the inventory client item shape.                                           |
| ✅ Already serialized | `DELETE` | `/inventory/items/{item_id}`                    | Archive an inventory item.                                                                            | No body is expected; handler returns `None` with `204 No Content`.                                                                               |
| ✅ Already serialized | `POST`   | `/inventory/movements`                          | Record a stock movement, rejecting invalid movements and changes that would result in negative stock. | Explicit `response_model=InventoryMovementResponse`; returns a typed movement schema with a nested item reference.                               |
| ✅ Already serialized | `POST`   | `/inventory/movements/{movement_id}/correction` | Correct a movement by recording a compensating movement.                                              | Explicit `response_model=InventoryMovementCorrectedEvent`; returns typed original and compensating movements, each with a nested item reference. |

All inventory routes require the inventory-manager dependency.

## Dashboard Aggregator API

Route definitions: [`services/dashboard-aggregator-api/main.py`](../services/dashboard-aggregator-api/main.py)

| Status                | Method | Route        | Purpose                                          | Response behavior                                                               |
| --------------------- | ------ | ------------ | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| ✅ Already serialized | `GET`  | `/health`    | Return the service health status.                | Explicit `response_model=HealthResponse`.                                       |
| ✅ Already serialized | `GET`  | `/dashboard` | Return dashboard metrics and operational panels. | Explicit `response_model=DashboardResponse` with typed metric and panel fields. |

No declared endpoint returns a raw ORM object. SQLite-backed incident and inventory results are converted to typed Pydantic schemas. The incident response projections omit database and audit metadata not consumed by the current UI contract.

## Sensitive Response Data

- No register, login, forgot/reset-password, or `/auth/me` routes currently exist under `services/`.
- Current response schemas contain no password/hash, email-address, or token fields.
- Inventory movement responses return a minimal nested item reference instead of a top-level `item_id`; correction responses nest both movements.
- Audit responses retain `actor_id` for attribution. The services do not define a nested user profile response, so no corresponding nested object is available.

## Relationship Response Decisions

| Relationship or field                                 | Endpoints                                            | Response decision                                                                    | Rationale                                                                                                                                   |
| ----------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Incident list entries and detail incident             | `GET /incidents`, `GET /incidents/{incident_id}`     | Return full client-facing `IncidentResponse` objects.                                | The list/detail views consume the incident fields; database and audit-only metadata is excluded.                                            |
| Incident creator/updater (`created_by`, `updated_by`) | Incident create and update responses                 | Omit the related IDs.                                                                | These are foreign keys to back-office users, are not required by the UI, and audit events preserve attribution for workflow changes.        |
| Audit event actor (`actor_id`)                        | `GET /incidents/{incident_id}` and `/history`        | Return only the actor ID.                                                            | Attribution is required for the audit trail, but no nested user profile response exists. The column is not a declared database foreign key. |
| `client_account`                                      | Incident responses                                   | Return as a flat scalar.                                                             | The database stores it as text, not as a foreign key to an account entity, so there is no related object to nest.                           |
| Inventory movement item                               | `POST /inventory/movements` and movement corrections | Return a nested flat projection: `item` with `id`, `name`, and `unit`.               | These fields provide useful movement context without returning the full item record; the raw response `item_id` is omitted.                 |
| Corrected movement pair                               | `POST /inventory/movements/{movement_id}/correction` | Return full nested `original_movement` and `compensating_movement` response objects. | Both movements explain the correction; raw `original_movement_id` and `compensating_movement_id` are omitted from the response.             |

Movement creation requests still accept `item_id` as the input selector; the ID-only choice applies to the request, not the response body.

## FastAPI Documentation Routes

Each app uses FastAPI's default documentation settings, which also provide `GET /openapi.json`, `GET /docs`, `GET /docs/oauth2-redirect`, and `GET /redoc`. These are framework-generated routes, not explicitly declared business endpoints, so they are excluded from the count above.

## Session Log

### 2026-10-21: Response Serialization and Exposure

- **Endpoint inventory:** Documented all 20 declared FastAPI routes across the incident API, inventory API, and dashboard aggregator, including methods, paths, purposes, response models, and serialization statuses.
- **Explicit response models:** Added typed health and catalog models, tightened incident response projections and severity-key typing, and added typed dashboard metric/panel models. All route decorators now declare `response_model`; the inventory archive route explicitly uses `response_model=None` for its empty `204` response.
- **Sensitive fields:** Confirmed that no register, login, password-reset, or `/auth/me` routes currently exist under `services/`, and no response schema exposes password/hash, email-address, or token fields. Incident creator/updater IDs remain omitted from response projections.
- **Relationship shapes:** Kept audit actor attribution as an ID because no nested user profile is available; kept `client_account` flat because it is stored as text; returned inventory movement items as a minimal nested `{id, name, unit}` projection; returned corrected movements as nested original and compensating movement objects.
- **Client alignment:** Updated the incident UI types for nullable response values. Updated the inventory movement client type and cache invalidation to use `movement.item.id`; movement creation requests still use `item_id` as the selector.
- **Validation:** The incident contract test passed; OpenAPI generation was checked for the incident, inventory, and dashboard APIs; dashboard payload validation, inventory movement mapper serialization, and incident/inventory UI typechecks passed. File diagnostics found no issues in the final documentation or inventory movement changes.
