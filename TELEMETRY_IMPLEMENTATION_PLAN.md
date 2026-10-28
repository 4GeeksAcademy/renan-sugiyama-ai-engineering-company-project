# Telemetry Persistence Implementation Plan

Status: Tasks 1.1 (inspection), 1.3 (PostgreSQL setup/schema confirmation), and 1.4 (database creation and verification) completed on 2026-10-26; Tasks 1.2 (event mappings), 2.1 (partial batch validation), 2.2 (event-to-row mapping), 2.3 (bulk persistence), 2.4 (focused backend verification), 3.1 (real workflow event generation), 3.2 (PostgreSQL event/schema audit), and 3.3 (manual partial-rejection verification) completed on 2026-10-28. Events without an explicitly assigned service map to `null`. Migrations 001 and 002 have been applied; the nullable service column was verified with the ingestion role. Real inventory, technical, and partial-rejection events were verified in PostgreSQL. No frontend code has changed.

## Confirmed Scope

- Implement PostgreSQL telemetry persistence behind the existing `POST /telemetry/events` endpoint.
- Keep the existing `{ "events": [...] }` request envelope and reuse `TelemetryEvent` unchanged.
- Validate individual events and persist valid, nonduplicate events in one bulk insert and one transaction per nonempty insert batch.
- Return `{ "received": N, "stored": M, "rejected": R }` after persistence succeeds.
- Change no frontend lines or frontend endpoint configuration.
- Verify existing inbound and outbound stock movements, not new order entities.
- Treat stored events as immutable: no application UPDATE or DELETE paths.

### Explicit Clarifications Superseding the Original Request

- The final table has **six columns**, not the originally mentioned eight: `id`, `event_type`, `timestamp`, `service`, `tags`, and `level`.
- `id` is a normal database row identifier, separate from the telemetry event identifier.
- Store envelope `eventId` as the reserved `event_id` key inside `tags`.
- Construct `tags` from the validated event's allowlisted `properties`, plus that reserved key. Do not add arbitrary payload fields.
- Derive `service` through an explicit backend mapping for every supported event type. The approved frontend-origin rules are `uis/backoffice/dashboard` -> `dashboard`, `uis/backoffice/incident-manager` -> `incident`, `uis/backoffice/inventory-manager` -> `inventory`, and `uis/website` -> `website`. The explicitly approved exception is `user_authentication_denied` -> `auth`, regardless of emitting frontend. Events without an explicitly assigned service must use `null`; do not infer one. These rules supersede the original backend-folder naming rule.
- Derive `level` through an explicit backend mapping for every supported event type; only `info` and `error` are allowed.
- Do not infer any event's service or level. Use `null` for an event without an explicitly assigned service, and use the explicitly approved `info`/`error` level mapping.
- Count duplicate event IDs as rejected, both within a request and across requests.
- PostgreSQL types and constraints below were proposed and explicitly approved during Task 1.3; they have not been applied to a database.

## Phase 1: Approve Contracts and Create the Table

### Task 1.1: Inspect the Existing Telemetry Path

- Locate the current handler, unchanged `TelemetryEvent` model, validation constants, persistence conventions, and runtime configuration under `services/`.
- Read `docs/telemetry/event-schemas.json` and `docs/telemetry/telemetry-plan.md` before implementation.
- Record the existing endpoint URL, routing/proxy behavior, and applicable CORS/authentication behavior without changing them.
- Inspect frontend configuration read-only to confirm the actual value and usage of `NEXT_PUBLIC_TELEMETRY_ENDPOINT`, or the existing equivalent if that variable is absent. Do not assume a URL or introduce a new variable.
- Verify that the existing TelemetryService uses HTTP status rather than the response body to determine success. Record any discrepancy as a blocker to transparent substitution.

#### Task 1.1 Findings (2026-10-26)

- **Handler and model:** `services/telemetry-api/app/routers/telemetry.py` defines `TelemetryEventType`, `TelemetryEvent`, `TelemetryBatch`, and `receive_events`. The `/telemetry` router prefix plus `/events` POST route produces `/telemetry/events`. The stub logs event types and returns only `{ "received": N }`; it has no persistence calls.
- **Existing validation:** `TelemetryEvent` forbids extra envelope fields, parses UUID identifiers and timezone-aware timestamps, constrains `schemaVersion` to `1.0.0`, and uses an event-type enum. However, `properties` is an unconstrained `dict[str, Any]`. `TelemetryBatch.events` is currently `list[TelemetryEvent]`, so FastAPI validates the entire batch before the handler executes.
- **Approved documents:** Reviewed `docs/telemetry/event-schemas.json` and `docs/telemetry/telemetry-plan.md`. The schema defines event-specific property allowlists; the processing plan requires event-ID deduplication and explicitly describes stock movements rather than order entities. No approved documents were changed.
- **Service configuration:** `services/telemetry-api/app/constants.py` reads `TELEMETRY_ENDPOINT`. `app/main.py` stores it in `app.state.telemetry_endpoint`; it does not use that value to set the route, bind a port, proxy requests, or configure persistence.
- **Local runtime:** `start-all.sh` starts telemetry with `python -m uvicorn app.main:app --app-dir services/telemetry-api --reload --reload-dir services/telemetry-api --port 8000`. The configured local endpoint is `http://localhost:8000/telemetry/events`. This records script/configuration evidence, not a live-server availability check.
- **Frontend configuration, read-only:** Both `uis/backoffice/dashboard/.env.local` and `uis/backoffice/inventory-manager/.env.local` explicitly set `NEXT_PUBLIC_TELEMETRY_ENDPOINT=http://localhost:8000/telemetry/events`. Other frontend applications' active endpoint values were not established. No endpoint variables or frontend files were changed.
- **Client routing:** `packages/telemetry/src/index.ts` sends directly to `NEXT_PUBLIC_TELEMETRY_ENDPOINT`. Inventory's `vite.config.ts` loads the Next.js-style variable and injects it into the shared client at build/dev-server startup; that configuration defines no telemetry proxy. No telemetry rewrite/proxy was found in the searched frontend Next.js/Vite configuration files.
- **CORS:** `app/main.py` allows origins `http://localhost:3000`, `http://localhost:3001`, `http://localhost:5173`, and `http://localhost:5174`, with method `POST` and header `Content-Type`. It does not enable CORS credentials. Browser-level cross-origin delivery was not exercised in this inspection.
- **Authentication:** The telemetry application and handler declare no authentication middleware/dependency; the in-memory POST succeeds without authentication headers. This finding applies to the inspected application, not any uninspected deployment gateway.
- **Client response compatibility:** `sendBatchWithRetry` in `packages/telemetry/src/index.ts` checks `response.ok` and never parses the response body. Adding `stored` and `rejected` is therefore compatible with this fetch path. The client batches up to 20 events, schedules a flush after 10 seconds, and allows three retries after the initial attempt. Its visibility-change path uses `navigator.sendBeacon`, which reports browser queue acceptance rather than an HTTP response; no application-level response body is consumed there either.
- **Persistence conventions:** No database module or migration directory exists in the inspected telemetry service. The neighboring inventory `app/db.py` uses SQLite connections, a `schema_migrations` ledger, sorted SQL migrations, and an explicit commit. Incident `app/db.py` also references SQLite and SQL migrations. These are existing business-service conventions, not a PostgreSQL implementation to reuse unchanged.
- **Compose scope:** Root `docker-compose.yml` defines frontend interfaces and the dashboard-aggregator backend. It does not currently define a telemetry service or PostgreSQL service. PostgreSQL setup remains Task 1.3; no infrastructure was added.

Focused verification used an ad-hoc `FastAPI TestClient` probe with the workspace-selected `.venv/bin/python`; no test files were created and no database was touched:

| Probe                                                         | Observed result               |
| ------------------------------------------------------------- | ----------------------------- |
| Single envelope-valid event with an unregistered property key | HTTP 200, `{ "received": 1 }` |
| Same event plus an invalid event                              | HTTP 422 for the entire batch |
| Empty events array                                            | HTTP 200, `{ "received": 0 }` |
| Missing events array                                          | HTTP 422                      |
| Direct model validation of the unregistered property key      | Accepted and retained         |
| Registered route dependencies                                 | Empty list                    |

**Property-validation finding and subsequent decision:** The unchanged model does not enforce the approved property allowlists. Reusing it alone cannot satisfy strict tag validation. During Task 1.2, separate JSON Schema validation alongside `TelemetryEvent.model_validate` was explicitly approved, leaving the model unchanged. No additional validator or model modification has been implemented.

**Inspection limits:** Live endpoint availability, browser CORS/beacon delivery, externally supplied environment overrides, and deployment-level authentication were not verified. The TestClient emitted a Starlette/httpx deprecation warning but completed successfully; dependencies were not changed.

### Task 1.2: Approve the Full Event Mapping

- Enumerate every registered `event_type` from the approved schema and compare it with the existing model's supported events.
- Prepare an explicit table with one row per supported event: `event_type`, source `service`, and `level`.
- Obtain approval of every assignment before implementing the mapping. Do not infer assignments from event names or from which service receives the batch.
- Confirm every mapped service matches the approved frontend-origin rules or an explicitly approved exception, and every level is `info` or `error`.
- Verify that the unchanged model enforces the approved event-specific property allowlists. If it does not, stop and resolve the discrepancy without silently modifying the model or accepting arbitrary tags.
- Inventory dimensions actually present in the approved schema and plan, including department, channel, or other event-specific fields where defined. Preserve those fields exactly in `tags`.
- Do not invent warehouse, office, or other location fields. Require an explicit contract decision if such dimensions are required but absent from the approved schema.

#### Task 1.2 Decisions and Completion (updated 2026-10-28)

- Runtime comparison confirms the schema catalog and backend `TelemetryEventType` enum each contain the same 24 event types, with no missing or additional entries.
- All 24 levels below were explicitly assigned by the user: 19 `info` and 5 `error`. Do not infer levels from severity, HTTP status, or event-name patterns.
- Service assignments marked `inventory` below follow the approved frontend-origin rule and the existing emitters inspected in `uis/backoffice/inventory-manager/src/api/inventoryClient.ts` and `movementTelemetry.ts`. The `auth` assignment is an explicit user exception. On 2026-10-28, the user specified that event types without an explicit service assignment must map to `null`; this does not infer service ownership.

| Event Type                             | Service     | Approved Level |
| -------------------------------------- | ----------- | -------------- |
| `website_visit_recorded`               | `website`   | `info`         |
| `marketing_conversion_completed`       | `null`      | `info`         |
| `sales_crm_coverage_snapshot_recorded` | `null`      | `info`         |
| `employee_departure_recorded`          | `null`      | `info`         |
| `workforce_snapshot_recorded`          | `null`      | `info`         |
| `employee_absence_recorded`            | `null`      | `info`         |
| `internal_requisition_opened`          | `null`      | `info`         |
| `internal_role_filled`                 | `null`      | `info`         |
| `support_ticket_resolved`              | `null`      | `info`         |
| `support_queue_snapshot_recorded`      | `null`      | `info`         |
| `support_query_closed`                 | `null`      | `info`         |
| `support_dissatisfaction_detected`     | `null`      | `info`         |
| `support_ticket_escalated`             | `null`      | `info`         |
| `department_kpi_snapshot_recorded`     | `null`      | `info`         |
| `kpi_threshold_triggered`              | `null`      | `info`         |
| `user_authentication_denied`           | `auth`      | `error`        |
| `stock_movement_validation_failed`     | `inventory` | `error`        |
| `direct_stock_edit_rejected`           | `null`      | `error`        |
| `outbound_stock_blocked`               | `inventory` | `error`        |
| `stock_movement_recorded`              | `inventory` | `info`         |
| `stock_threshold_triggered`            | `inventory` | `info`         |
| `stock_movement_correction_recorded`   | `null`      | `info`         |
| `api_latency_recorded`                 | `inventory` | `info`         |
| `api_request_failed`                   | `inventory` | `error`        |

**Approved validation approach:** Validate each raw event against the existing Draft-07 JSON Schema, including format checking, in addition to per-event `TelemetryEvent.model_validate`. Reject a failing item without cancelling its batch. The `jsonschema` library was not installed in the selected workspace interpreter during inspection; dependency setup and validator implementation remain future tasks. Validate the original envelope event before adding the storage-only `event_id` key to tags, so the approved property allowlists remain unchanged.

**Confirmed property dimensions:** All 24 event property definitions set `additionalProperties: false`. Preserve each event's complete approved properties object, not only selected analytical labels. Existing grouping dimensions include `trafficSource`, `medium`, and `campaignId` for website/marketing events; `department` for employee/workforce/requisition/KPI events; `roleFamily` for requisitions; `channel` for ticket resolutions; `queueId` for queue snapshots; `resolutionMethod` for query outcomes; `riskLevel` for dissatisfaction; `escalationType` and `escalationReasonCategory` for escalations; `metricName`, `unit`, and `severity` where defined for KPI events; movement/category/unit fields where defined for inventory events; and route/method/status/error categories where defined for technical events. No `warehouse` or `office` property is defined in the approved schema. Do not add either without an explicit contract change.

**Service default approved (2026-10-28):** All previously pending service entries now map to `null` until an explicit service is approved. The generic API events retain their explicit `inventory` assignments as recorded above; no future service ownership is inferred from those assignments.

**Task 1.2 completed (2026-10-28):** The approved service and level table now has an explicit value for all 24 event types, using `null` where no service is assigned. The event schema and existing telemetry model still cover the same 24 types.

### Task 1.3: Confirm PostgreSQL Setup and Schema Proposals

Column definitions explicitly approved during Task 1.3, not yet applied:

| Column       | Proposed PostgreSQL type/constraint                                 | Source                                                                         |
| ------------ | ------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `id`         | `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`                   | Database-generated row ID                                                      |
| `event_type` | `TEXT NOT NULL`                                                     | Validated `event_type`                                                         |
| `timestamp`  | `TIMESTAMPTZ NOT NULL`                                              | Validated occurrence timestamp; preserve the instant, use UTC for verification |
| `service`    | `TEXT` (nullable)                                                   | Approved backend event-to-service mapping; `null` when no service is assigned  |
| `tags`       | `JSONB NOT NULL`, constrained to an object with a string `event_id` | Validated `properties` plus `event_id` from envelope `eventId`                 |
| `level`      | `TEXT NOT NULL CHECK (level IN ('info', 'error'))`                  | Approved backend event-to-level mapping                                        |

- Confirm the PostgreSQL connection settings, driver, pooling/lifecycle approach, and schema initialization mechanism using the nearest existing project conventions.
- Keep existing business-service SQLite persistence outside this change; do not migrate business tables.
- Keep secrets out of tracked files and verification evidence.
- Identify whether a new migration or any protected documentation change is needed. Obtain explicit approval before changing anything under `services/**/migrations/`, `memory-bank/`, or other protected paths.
- Confirm the proposed row ID/type choices and JSONB constraints before applying DDL.

#### Task 1.3 Confirmed Configuration (2026-10-26)

**Inspection evidence:** Terminal PATH contains Docker, `psql`, and `pg_isready`; PostgreSQL tools are supplied by Postgres.app. Availability alone does not prove a server or Docker daemon is running. The selected workspace `.venv/bin/python` has none of `psycopg`, `psycopg_pool`, `psycopg2`, `asyncpg`, or `sqlalchemy` installed. In that interpreter process, `DATABASE_URL`, `TELEMETRY_DATABASE_URL`, `PGHOST`, and `PGDATABASE` were unset. No secret values were read or recorded.

The existing `services/Dockerfile` installs only the dashboard-aggregator requirements and starts that API. Telemetry has no existing requirements file in the inspected service; neighboring services use service-local `requirements.txt` files. Preserve their dependencies and SQLite databases.

The user explicitly approved the following configuration:

| Setting                       | Approved Value                                                                                                          |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| PostgreSQL runtime            | New container using `postgres:17`                                                                                       |
| Compose service               | `telemetry-postgres`                                                                                                    |
| Host binding                  | `127.0.0.1:5433` -> container port `5432`                                                                               |
| Database                      | `telemetry`                                                                                                             |
| Schema owner / migration role | `telemetry_owner`                                                                                                       |
| API ingestion role            | `telemetry_ingest`; no UPDATE or DELETE permissions                                                                     |
| Persistent named volume       | `telemetry_postgres_data`                                                                                               |
| API connection variable       | `TELEMETRY_DATABASE_URL`                                                                                                |
| Driver                        | Psycopg 3 with binary distribution                                                                                      |
| Pool                          | `psycopg_pool`; minimum 1, maximum 5 connections per API process                                                        |
| Pool lifecycle                | Open and close through FastAPI lifespan                                                                                 |
| Schema initialization         | Separate explicit migration step, never per request                                                                     |
| Column definitions            | All six PostgreSQL types and constraints in the Task 1.3 table approved                                                 |
| Protected-path permission     | Create a new SQL migration under `services/telemetry-api/migrations/` only; do not change existing protected migrations |

**Schema override and verification (2026-10-28):** The user approved `null` for events without an explicitly assigned service. Migration `002_allow_null_telemetry_service.sql` drops the `NOT NULL` constraint created by migration 001; migration 002 was applied without editing or rerunning migration 001. The information schema reports `service.is_nullable = YES`. An insert as `telemetry_ingest` with `service = NULL` succeeded inside a transaction, which was rolled back; a follow-up query confirmed zero persisted probe rows.

**Secret handling:** Configure database passwords locally outside tracked source. Do not request passwords through chat, place them in migration files, or include connection strings containing credentials in evidence. The approved host binding is for a host-run API; any future containerized API needs an explicitly confirmed internal connection target rather than assuming host loopback works inside a container.

**Deferred execution:** No container was started, no Compose or dependency files were edited, no Python package was installed, no roles were created, and no DDL was executed. Docker daemon readiness, image availability, host-port availability, database connectivity, and privilege enforcement remain unverified until provisioning. Establish concrete compatible dependency pins during dependency setup rather than claiming an untested version is installed.

Task 1.3 confirmation is complete. Task 1.4 provisioned the approved runtime and applied migration 001. The user subsequently approved its event-ID uniqueness index and explicitly authorized database-only work independently of Task 1.2's then-pending service assignments. The later null-service approval is documented under Task 1.2 and removes the event-service mapping gate.

### Task 1.4: Create the Append-Only Table and Indexes

- Create `telemetry_events` with the six approved columns before replacing the endpoint stub.
- Create the three requested analytical indexes: B-tree on `timestamp`, B-tree on `event_type`, and GIN on `tags`.
- Propose an additional unique expression index on `tags ->> 'event_id'` for concurrency-safe event-ID deduplication; approve it before implementation. The three analytical indexes alone do not provide uniqueness.
- Normalize validated event IDs consistently before storage and conflict checking so equivalent UUID representations cannot bypass deduplication.
- Do not add UPDATE, DELETE, upsert-update, replacement, or cleanup logic for stored telemetry.
- Propose a separate ingestion role limited to required INSERT privileges and minimal SELECT/sequence privileges needed for insertion and returned results; no UPDATE or DELETE privileges. Keep schema-owner privileges separate.

#### Task 1.4 Implementation and Verification (2026-10-26)

Additional explicit approvals: create the unique expression index on `tags ->> 'event_id'`; proceed with database-only work before completing service assignments; store local credentials in a root `.env.telemetry` file explicitly ignored by Git.

- `docker-compose.yml` now defines `telemetry-postgres` with the approved image, loopback port binding, database, named volume, and readiness healthcheck. Migration files are mounted read-only at `/migrations`; starting the database does not automatically apply them.
- `.gitignore` explicitly ignores `/.env.telemetry`. The local file contains `TELEMETRY_POSTGRES_PASSWORD`, `TELEMETRY_OWNER_PASSWORD`, and `TELEMETRY_INGEST_PASSWORD`, configured directly by the user outside chat. Owner-only permissions (`0600`) were set when creating the file, and Git ignore behavior was verified. No password values were displayed during provisioning. Compose rejects missing or empty values.
- `services/telemetry-api/migrations/001_create_telemetry_events.sql` is a new, separately executed psql migration. It creates the nonsuperuser `telemetry_owner` and `telemetry_ingest` roles, transfers database/schema ownership, creates all six columns, the three analytical indexes, and the approved unique event-ID index within one transaction. It reads role passwords from the container environment rather than embedding them in SQL.
- The standard container bootstrap role is `postgres`, separate from the nonsuperuser schema owner and ingestion role. `telemetry_ingest` receives database CONNECT, schema USAGE, table INSERT, column SELECT on `id` and `tags`, and identity-sequence USAGE. It receives no UPDATE, DELETE, TRUNCATE, ownership, or role-management privileges. Restricted-role execution and catalog checks confirmed these mutation/elevation restrictions against PostgreSQL.
- No existing protected migration was changed. No backend pool, dependency installation, endpoint logic, model, frontend file, or business-service database was changed in this step.

**Validation completed:** `docker compose --env-file .env.telemetry config --quiet` passed with nonsecret configuration-validation-only environment overrides; no container was started with those values. `git diff --check`, Git ignore verification, and editor diagnostics passed. Editor diagnostics are not proof that PostgreSQL accepts or enforces the migration.

**Provisioning completed:** After the user started Docker and configured passwords locally, Docker readiness and Compose validation succeeded. The approved `postgres:17` image started successfully and the service became healthy. The running server reports PostgreSQL `17.11`. A read-only preflight confirmed that the table and application roles did not already exist, then the migration ran once and committed successfully. The persistent volume was not reset or removed.

Commands executed successfully:

```bash
docker compose --env-file .env.telemetry up -d --wait telemetry-postgres
docker compose --env-file .env.telemetry exec -T telemetry-postgres psql -U postgres -d telemetry -f /migrations/001_create_telemetry_events.sql
```

**Live verification completed:**

- PostgreSQL metadata confirms all six columns, their NOT NULL constraints, `TIMESTAMPTZ` occurrence time, JSONB tags, and the generated identity ID.
- Index metadata confirms the three analytical indexes, unique event-ID expression index, and primary-key index (five indexes total).
- A focused transaction used `SET LOCAL ROLE telemetry_ingest` to insert two rows in one statement, proving insert and sequence privileges.
- Duplicate insertion with the expression-index conflict target and `DO NOTHING RETURNING id` returned no new ID; a duplicate without conflict handling raised `unique_violation`.
- JSONB arrays, missing `event_id`, null IDs, and numeric IDs raised constraint violations. An unsupported `warning` level was also rejected.
- Actual UPDATE, DELETE, and TRUNCATE attempts under the ingestion role each raised `insufficient_privilege`. Catalog checks confirmed neither application role has superuser, database/role creation, replication, or row-security bypass privileges, and ingestion has neither schema CREATE privileges nor membership in the owner role.
- The probe transaction was rolled back, and a subsequent query confirmed zero persisted event rows. PostgreSQL sequence values may still have advanced during the rolled-back insert probes.

Task 1.4 was complete on 2026-10-26. At that point, live checks used local administrative access with a restricted-role switch; API authentication, UUID normalization, and endpoint persistence remained future work. Do not rerun the one-time migration against this initialized database.

**Follow-up (2026-10-28):** Task 1.2 service mappings and Task 2.2 row mapping are complete. Task 2.3 verified password-authenticated API pool access and persisted events using canonical Pydantic UUID values. Task 2.4 focused backend verification is complete; see its results below.

Phase 1 exit criteria: mappings and SQL proposals approved; PostgreSQL table, analytical indexes, and deduplication constraint verified; no mutation paths introduced.

## Phase 2: Replace the Stub with Partial Validation and Bulk Persistence

### Task 2.1: Parse the Envelope Without Eager Item Validation

- Preserve the existing route and envelope while validating only that the outer body contains an `events` array.
- Keep array entries raw until the handler processes them. Do not declare `events: list[TelemetryEvent]` or use a raw-dictionary list type that rejects nondictionary entries before the handler runs.
- Call `TelemetryEvent.model_validate(raw)` inside the handler for each entry, catching `ValidationError` per item and continuing with the remaining entries.
- Count malformed entries, including nonobjects, as individually rejected rather than rejecting an otherwise parseable batch.
- Preserve the existing malformed-envelope error contract where defined; establish it explicitly if absent. Partial acceptance applies to event failures, not malformed JSON or a missing/nonarray `events` envelope.

#### Task 2.1 Implementation and Verification (2026-10-28)

- Changed `TelemetryBatch.events` to retain raw entries until the handler processes them; the existing `TelemetryEvent` model remains unchanged.
- The handler now validates each entry with `TelemetryEvent.model_validate`, catches `ValidationError` per entry, counts rejected entries, and logs only aggregate rejection counts and valid event types.
- A focused FastAPI probe confirmed a batch containing one valid event, one invalid object, and one nonobject returns HTTP 200 without whole-batch validation failure. Missing and non-array `events` envelopes still return HTTP 422.
- The response remains `{ "received": N }`; persistence and externally returned `stored`/`rejected` counts remain for Task 2.3. No frontend files changed.

### Task 2.2: Map Validated Events to Rows

- Use the unchanged validated model as the source of event type, timestamp, properties, and event ID.
- Resolve `service` and `level` exclusively from the complete approved mappings.
- Serialize validated properties with the existing structured serialization tools, preserving JSON value types and event-specific dimensions.
- Add the reserved `event_id` key from envelope `eventId`; do not copy other envelope fields or unapproved properties into tags.
- Ensure no credentials, personal content, arbitrary exception text, or other excluded data is stored or logged.

#### Task 2.2 Implementation and Verification (2026-10-28)

- The handler validates each raw event against the approved Draft-07 schema with format checking, in addition to the unchanged `TelemetryEvent` model. Events with unapproved properties are counted as rejected.
- The approved schema is copied to `services/telemetry-api/app/event-schemas.json`; runtime validation loads this package-local file and has no dependency on the repository `docs/` directory. The copy was verified byte-for-byte against the approved catalog.
- Added `jsonschema[format]` to the telemetry API requirements. Explicit service and level maps cover all 24 event types; event types without an approved service use `null`.
- `map_event_to_row` preserves the validated properties in `tags`, adds only the canonical envelope event ID as `event_id`, and maps the validated event type, timestamp, nullable service, and approved level.
- Focused probes confirmed schema rejection without payload logging, complete mapping coverage, null services, approved levels, and structured tags. No persistence or frontend changes were made; Task 2.3 remains next.

### Task 2.3: Insert Once and Count Actual Outcomes

- Collect mapped rows, then perform one parameterized multi-row INSERT in one transaction. Do not loop over INSERTs, open one transaction per event, or assume a driver `executemany` call is one SQL statement.
- Handle event-ID uniqueness conflicts with insert-only conflict handling, never by updating an existing event. Use the unique expression index to protect concurrent requests as well as sequential retries.
- Count actual inserted rows using returned results or reliable driver row counts. Duplicates, including those in the same batch, increment `rejected` and leave existing rows unchanged.
- Confirm that duplicate conflicts do not cancel insertion of other valid, distinct events in the same batch.
- Set `received` to the original array length, `stored` to newly persisted rows, and `rejected` to validation failures plus duplicates. For successful requests, require `received = stored + rejected`.
- If the batch is empty or has no eligible rows, skip database insertion and return HTTP 200 with the correct zero/nonzero counts.
- Return HTTP 200 after successful processing of a parseable envelope, including mixed or entirely rejected event batches.
- On a database/transaction failure, roll back and return the applicable non-2xx failure response. Do not report successful storage or classify infrastructure failures as invalid events.

#### Task 2.3 Implementation and Verification (2026-10-28)

- Added Psycopg 3 and `psycopg_pool` dependencies. FastAPI lifespan opens and closes a synchronous connection pool with the approved minimum of 1 and maximum of 5 connections, using `TELEMETRY_DATABASE_URL`.
- Updated `start-all.sh` to derive and export the connection URL from Compose's parsed `.env.telemetry` configuration when it is not already set. Credential values are not printed.
- Added `app/db.py` with one parameterized multi-row `INSERT` per nonempty batch, JSONB adaptation, `ON CONFLICT ((tags ->> 'event_id')) DO NOTHING`, and `RETURNING` to count rows actually stored. The pool connection context commits on success and rolls back on error.
- The endpoint now returns `{ "received": N, "stored": M, "rejected": R }`; validation failures and duplicate IDs contribute to `rejected`. Persistence failures return HTTP 503 with a generic detail and no payload logging.
- Live endpoint verification: a batch with a duplicate event and one invalid event returned `{ "received": 3, "stored": 1, "rejected": 2 }`; retry returned `{ "received": 3, "stored": 0, "rejected": 3 }`. A mixed batch with a duplicate, a distinct valid event, and an invalid event returned `{ "received": 4, "stored": 2, "rejected": 2 }`.
- Closing the pool during a request returned HTTP 503. A PostgreSQL check-constraint failure propagated from the insert helper and rolled back; a follow-up query confirmed zero rows for that probe ID. Three synthetic `website_visit_recorded` rows from successful endpoint probes remain in the local append-only database.
- Focused helper verification confirmed one multi-row statement, five bound parameters per row, returned-row counting, and no DB connection for an empty batch. Task 2.4 verification results are recorded below.

### Task 2.4: Perform Focused Backend Verification

- Use existing focused checks or manual requests; add new automated tests only if separately requested.
- Verify valid-only, mixed-validity, all-invalid, empty, and nonobject-item batches.
- Verify missing/nonarray envelopes and malformed JSON remain distinct from per-event rejection.
- Verify repeated event IDs within one batch, across requests, and in concurrent requests do not produce duplicate rows or change existing records.
- Verify a representative 20-event batch produces one multi-row INSERT and one commit, not 20 INSERTs. Inspect driver tracing or PostgreSQL statement evidence in a local environment without exposing payloads.
- Verify database failure rolls back and never produces a misleading HTTP 200 success count.
- Confirm the model and frontend diffs remain empty and the existing client accepts the success status without depending on response fields.

#### Task 2.4 Verification Results (2026-10-28)

- Valid-only returned `{ "received": 1, "stored": 1, "rejected": 0 }`; mixed validity with one valid event, one schema-invalid event, and one nonobject returned `{ "received": 3, "stored": 1, "rejected": 2 }`; all-invalid returned `{ "received": 2, "stored": 0, "rejected": 2 }`; empty returned all zero counts.
- Missing `events`, non-array `events`, and malformed JSON each returned HTTP 422, distinct from per-event rejection in an otherwise valid envelope.
- Same-batch and cross-request duplicates were rejected without replacing prior rows. Five concurrent requests with the same event ID produced exactly one stored row; a query confirmed its properties matched the winning request.
- A 20-event duplicate batch produced one observed cursor `execute`, 100 bound parameters, and one successful pool connection context; the existing duplicate ID avoided creating additional test rows. Psycopg's pool context commits once on successful exit.
- A database check-constraint failure rolled back and left no row for its probe ID; a closed pool returned HTTP 503 rather than success.
- `TelemetryEvent` remained unchanged; no frontend or shared telemetry client files changed. The client checks `response.ok` and does not parse the response body. Three additional synthetic website events from these probes remain in the local append-only database, six total from Tasks 2.3 and 2.4.
- No automated test files were added. Focused Python diagnostics, launcher syntax, and whitespace checks passed.

Phase 2 exit criteria: the same endpoint partially accepts batches, maps every supported event explicitly, bulk-inserts immutable records, and returns accurate counts with no model or frontend edits.

## Phase 3: Verify Real Events End to End

### Task 3.1: Generate Events Through Existing Workflows

- Run the real telemetry endpoint with PostgreSQL and the existing backoffice configuration.
- Record one successful inbound stock movement and one successful outbound stock movement using the inventory UI. Use these existing operations as the approved interpretation of inbound/outbound orders.
- Generate at least one real technical event through an existing instrumented workflow, such as a failed login or API error.
- Observe existing emitter/flush behavior and correlate operations with telemetry requests without changing frontend code or adding new instrumentation.
- If a required workflow does not emit its documented event, record a blocker and seek explicit authorization for any instrumentation work outside this scope.

#### Task 3.1 Results (2026-10-28)

- Started the telemetry API, inventory API, and inventory manager UI with the existing local configuration. Used the existing inventory item `teste`; no item or instrumentation code was added.
- The first UI page was opened at `http://127.0.0.1:5173`, which is not in the telemetry API's CORS allowlist. An initial inbound movement of 3 units succeeded in the inventory API, but the browser's telemetry request failed preflight and no matching telemetry row was persisted.
- Reopened the UI at the allowed `http://localhost:5173` origin. Recorded an inbound movement of 1 unit (`movementId` `6bd9af80-4f42-4d54-be03-6d42b0f9b495`, stock 80 to 81) and an outbound movement of 1 unit (`movementId` `9139532b-7d70-42ea-9586-1170d9d604a0`, stock 81 to 80).
- The foreground telemetry POST returned HTTP 200 with a six-event batch containing both `stock_movement_recorded` events and API latency events. PostgreSQL rows were correlated by `tags.event_id` and `tags.movementId`; both have UTC timestamps, `service = inventory`, `level = info`, and the expected movement type, quantity, and stock values.
- Submitted an outbound quantity of 999 through the same UI to produce an expected HTTP 409 without changing stock. The UI showed “Movement would produce negative stock”; the telemetry batch contained `api_request_failed` and `outbound_stock_blocked`. PostgreSQL confirms both as `service = inventory`, `level = error`; the failure event records route `/inventory/movements`, status 409, and error code `conflict`. Current stock remains 80.
- A browser page-hide telemetry request was also rejected by CORS because that request used credentials mode `include` while the telemetry API does not return `Access-Control-Allow-Credentials`. Normal foreground fetch batches succeeded from the allowlisted `localhost` origin. This beacon-path limitation is recorded for follow-up; no CORS, frontend, or instrumentation code was changed.

### Task 3.2: Inspect PostgreSQL Directly

- Query `telemetry_events` using a read-only inspection connection and correlate rows by `tags ->> 'event_id'`.
- Confirm both stock directions and the technical event are persisted with correct `event_type`, occurrence `timestamp`, approved `service`, approved `level`, and structured `tags`.
- Confirm `tags` preserves each event's actual allowlisted properties and dimensions, with only the explicitly authorized reserved `event_id` addition.
- Inspect table metadata and index definitions directly; verify six columns, the three analytical indexes, and the separately approved uniqueness index.
- Verify ingestion permissions and application code contain no telemetry UPDATE or DELETE capability.

#### Task 3.2 Results (2026-10-28)

- Read-only PostgreSQL metadata confirms six columns: generated `BIGINT` ID, text event type, `TIMESTAMPTZ`, nullable text service, JSONB tags, and text level. Five indexes exist: primary key, timestamp, event type, GIN tags, and unique `tags ->> 'event_id'`.
- The correlated inbound and outbound `stock_movement_recorded` rows were queried by envelope `event_id` and `movementId`. Each has eight tag keys total: the seven schema-approved movement properties plus `event_id`; values, UTC occurrence timestamps, `service = inventory`, and `level = info` match the UI operation.
- The `api_request_failed` and `outbound_stock_blocked` rows were also verified. Each has five approved event properties plus `event_id`; both are `inventory`/`error`, with route/status/error category or blocked-quantity fields as defined by the schema.
- `telemetry_ingest` has INSERT and identity-sequence USAGE, SELECT only on `id` and `tags`, and no UPDATE, DELETE, or TRUNCATE privileges. `telemetry_owner` and `telemetry_ingest` are not superusers and have no database/role creation, replication, or row-security bypass privileges.
- A search of telemetry application source found no UPDATE, DELETE, TRUNCATE, or upsert-update path. Matches for `DELETE` are only HTTP method values in the event schema, not database mutation logic. All audit queries ran in read-only transactions; no data was changed.

### Task 3.3: Verify Manual Partial Rejection

- Send a manual request to the unchanged endpoint with two valid, distinct events and one event that violates the unchanged model.
- Expect HTTP 200 and `{ "received": 3, "stored": 2, "rejected": 1 }`; query PostgreSQL to confirm exactly the two valid events were newly stored.
- Resend the same payload and expect `{ "received": 3, "stored": 0, "rejected": 3 }`: two duplicates plus one invalid event. Confirm prior rows remain unchanged.
- Record sanitized request/response counts, row-query evidence, and bulk-insert evidence without committing secrets or sensitive payloads.

#### Task 3.3 Results (2026-10-28)

- Sent two valid, distinct `website_visit_recorded` events and one event with an invalid UUID `eventId` to the live endpoint. The first request returned HTTP 200 with `{ "received": 3, "stored": 2, "rejected": 1 }`.
- Resent the identical payload. It returned HTTP 200 with `{ "received": 3, "stored": 0, "rejected": 3 }`, counting both existing event IDs as duplicates and the invalid UUID as rejected.
- A read-only PostgreSQL query found exactly the two valid event IDs, with their original approved properties, service, level, and occurrence timestamps intact; no row existed for the invalid ID. No payloads or credentials were committed.
- No frontend/model changes or automated test files were added.

Phase 3 exit criteria (completed 2026-10-28): real business and technical events are verified in PostgreSQL, partial rejection and deduplication are demonstrated, and the frontend remains unchanged.

## Final Validation Checklist

- [x] `telemetry_events` exists in PostgreSQL with the six explicitly confirmed columns, superseding the original eight-column requirement.
- [x] The timestamp, event-type, and GIN tags indexes exist; event-ID uniqueness is enforced through the separately approved mechanism.
- [x] Stored events have no application UPDATE/DELETE logic, and the ingestion role cannot mutate existing records.
- [x] Every supported event has an explicitly approved service and `info`/`error` level mapping.
- [x] `POST /telemetry/events` preserves the envelope and endpoint configuration and returns `received`, `stored`, and `rejected`.
- [x] Each raw event is validated inside the handler with `TelemetryEvent.model_validate`; a bad event cannot trigger whole-batch eager validation failure.
- [x] Valid, distinct events persist even when neighboring entries are invalid or duplicate.
- [x] The existing `TelemetryEvent` model is unchanged.
- [x] No frontend file or frontend endpoint configuration has changed.
- [x] Inbound and outbound stock movements and at least one real technical event appear with correct event types, timestamps, tags, services, and levels.
- [x] Tags preserve approved property allowlists and documented dimensions, plus the explicitly approved reserved `event_id`; no undocumented warehouse/office fields are invented.
- [x] Duplicate IDs count as rejected and do not overwrite prior records.
- [x] Every batch with eligible rows uses one bulk INSERT and one transaction, not one INSERT per event.
- [x] Database failures roll back and return non-2xx responses rather than false storage counts.
- [x] Focused verification evidence is recorded; any unverified item remains explicitly unchecked.

## Approval and Scope Boundaries

Implementation must wait for approval of the complete event mappings, proposed SQL types/constraints, deduplication index, and any required protected-path changes. Do not implement new order entities, frontend instrumentation, downstream analytics, stream processors, retention jobs, or unrelated refactors as part of this plan.
