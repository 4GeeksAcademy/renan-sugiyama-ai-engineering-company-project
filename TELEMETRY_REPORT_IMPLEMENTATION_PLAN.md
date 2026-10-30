# Telemetry Report Implementation Plan

## Scope and Fixed Decisions

- Implement in the existing FastAPI service under `services/telemetry-api`; do not create a parallel `services/telemetry` service.
- Report technical and operational activity only. Exclude website/marketing/sales, HR/workforce, and other business outcome metrics.
- `events_per_day` includes exactly these operational event types: `support_ticket_resolved`, `support_queue_snapshot_recorded`, `support_query_closed`, `support_dissatisfaction_detected`, `support_ticket_escalated`, `user_authentication_denied`, `stock_movement_validation_failed`, `direct_stock_edit_rejected`, `outbound_stock_blocked`, `stock_movement_recorded`, `stock_threshold_triggered`, `stock_movement_correction_recorded`, `api_latency_recorded`, and `api_request_failed`.
- `error_rate_by_type` means HTTP 5xx share by API request type, where request type is the normalized `method + routeTemplate`. For each UTC day and request type, divide 5xx latency measurements by all valid latency measurements for that group. HTTP 4xx responses are not server errors. One valid `api_latency_recorded` row represents one measured request; do not infer missing denominator rows from `api_request_failed` events.
- Use `tags.durationMs` as the latency value because it is required by the event schema; the top-level `value` column can be null. Group average latency by UTC day, route template, and method.
- Return only observed groups; do not synthesize zero-count dates or groups. Return empty lists when a metric has no valid rows. Drop rows with missing or invalid required dimensions/values before calculating that metric.
- Keep `docs/telemetry/telemetry-plan.md`, `docs/telemetry/event-schemas.json`, and protected migrations unchanged.

## Phase 1: Analysis Pipeline

### Task 1.1: Add dependency and analysis module

- Add Pandas to `services/telemetry-api/requirements.txt` using a bounded compatible version range.
- Create `services/telemetry-api/app/analysis.py` as the home for telemetry report analysis and define the operational event-type allowlist there.
- Leave metric functions, SQL loading, and Pandas transformations to Tasks 1.2 and 1.3 so this setup task does not introduce placeholder APIs.

### Task 1.2: Implement the three metrics

- Implement independent read-only metric functions that accept the report database pool and aware UTC `start_date` / `end_date` values. They must be deterministic for the same database snapshot and bounds.
- Use parameterized Postgres queries against `public.telemetry_events`. Every metric query must include `timestamp >= start_date AND timestamp < end_date` and its relevant `event_type` predicate, selecting only the fields needed by that metric. Do not load the whole table or apply another date-window filter in Pandas.
- Keep tag extraction and optional tag filtering in Pandas; do not push tags predicates into SQL for this implementation.
- `events_per_day(start_date, end_date, pool)`: query the exact operational event-type allowlist above; group counts by UTC date and `event_type`. Return records shaped as `date`, `event_type`, and `count`.
- `error_rate_by_type(start_date, end_date, pool)`: query `api_latency_recorded`; extract `routeTemplate`, `method`, and `httpStatus` from `tags`; build a server-error flag for status codes 500-599; group by UTC date, request type, and calculate `server_error_count / request_count`. Return the numerator, denominator, and fractional rate (0-1) so the result is auditable.
- `average_latency_by_endpoint(start_date, end_date, pool)`: query `api_latency_recorded`; extract `routeTemplate`, `method`, and `durationMs` from `tags`; coerce duration to numeric, discard missing/non-finite/negative values and missing route/method; group by UTC date, route template, and method; calculate the mean in milliseconds and include the valid sample count.
- For both latency-derived metrics, accept only integral `httpStatus` values from 100 through 599. The error-rate denominator includes valid status rows with valid route and method; its numerator is the subset with status 500-599. Missing/invalid rows are excluded from both numerator and denominator.

### Task 1.3: Enforce Pandas and serialization rules

- In every function, build the DataFrame from the SQL result and convert timestamps with `pd.to_datetime(df["timestamp"], utc=True)` before deriving a date or performing any temporal groupby.
- Extract dimensions from `tags`, drop rows with null required dimensions, and derive flags in Pandas before grouping and aggregation. Use Pandas operations for all metric calculations; do not use Python loops to calculate metrics.
- Convert output dates to `YYYY-MM-DD` strings and return `reset_index().to_dict(orient="records")` results containing only JSON-serializable scalar values. Empty input returns `[]`.

### Task 1.4: Configure report read access

- Use the existing `TELEMETRY_DATABASE_URL` connection pool for both ingestion and report queries; do not define a second report URL or pool.
- Add a new migration granting the existing `telemetry_ingest` role SELECT on `event_type`, `timestamp`, and `tags`. Preserve its existing INSERT and limited `id`/`tags` SELECT grants; do not grant UPDATE or DELETE.
- Have `start-all.sh` apply the additive, repeatable permission migration after the local telemetry database is ready and before the APIs start. Apply the same migration through the deployment's database migration process.

## Phase 2: Report Endpoint and Cache

### Task 2.1: Define date parameter behavior

- Implement `resolve_report_period(start_date, end_date, now=None)` in the telemetry router as a reusable period-normalization helper. Keep route registration until Task 2.3 so no uncached report endpoint is exposed.
- Accept optional timezone-aware ISO-8601/RFC 3339 datetimes. Require an explicit timezone (`Z` or numeric offset), normalize supplied bounds to UTC, and reject naive timestamps with HTTP 422.
- Capture `now` once per call and round it down to the current UTC minute so repeated default requests share a stable cache key. If both values are omitted, use `[now - 7 days, now)`. If only `start_date` is supplied, use the rounded `now` as the exclusive end. If only `end_date` is supplied, use `end_date - 7 days` as the inclusive start. Reject `start_date >= end_date` with HTTP 422.
- Return the exact normalized bounds for later metric calls and the cache key. The date window is inclusive at the start and exclusive at the end.

### Task 2.2: Build and serve the report

- Put orchestration in a separate `build_telemetry_report(start_date, end_date, pool)` function. It calls the three analysis functions and returns the metrics object; it must not contain Pandas transformations beyond those in the metric functions.
- Define the full response contract for the endpoint that Task 2.3 will register:

  ```json
  {
    "period": { "from": "UTC ISO-8601", "to": "UTC ISO-8601" },
    "metrics": {
      "events_per_day": [],
      "error_rate_by_type": [],
      "average_latency_by_endpoint": []
    }
  }
  ```

- Serialize `period.from` and `period.to` as UTC ISO-8601 timestamps; `period.to` is the exclusive end. Task 2.3 handles HTTP delivery and returns a sanitized HTTP 503 if the telemetry pool is unavailable or database access fails; do not expose SQL details or credentials.

### Task 2.3: Add the 60-second process-local cache

- Register `GET /telemetry/report` on the existing `/telemetry` router. Resolve query parameters with `resolve_report_period`, then return the cached report or call `build_telemetry_report` on a cache miss. The route must not calculate metrics inline.
- Cache the complete serialized report by the normalized UTC `(start_date, end_date)` pair. A matching unexpired entry is returned without invoking the report builder; a miss/expired entry invokes it once and stores the result for 60 seconds.
- Use a monotonic clock for expiry. Remove expired entries during lookup/store so arbitrary requested windows do not leave stale entries indefinitely.
- Keep this as an in-memory per-process cache; do not add Redis or claim cross-worker coherence. Ensure cache entries contain only JSON-safe report data.
- Return a sanitized HTTP 503 if the telemetry pool is unavailable or database access fails. Add `GET` to the existing CORS `allow_methods` so browser dashboards on configured origins can call the endpoint.

## Phase 3: Focused Tests and Completion Checks

### Task 3.1: Create analysis tests

- No telemetry API test directory currently exists. Create `services/telemetry-api/tests/test_analysis.py` and use a fake pool/cursor or equivalent controlled SQL-result fixture; do not require live Supabase credentials.
- Verify SQL timestamp bounds are inclusive-start/exclusive-end and event types are filtered in SQL; verify UTC conversion precedes temporal grouping, operational type counts, 5xx numerator/denominator, average latency/sample count, invalid/missing dimension handling, empty results, and JSON serialization.
- Include timestamps with different offsets that fall on the same UTC date to catch string-grouping and local-time errors.

### Task 3.2: Create endpoint and cache tests

- Create `services/telemetry-api/tests/test_report_endpoint.py` using FastAPI `TestClient` and replaceable report-builder/pool dependencies.
- Verify default dates, both supplied bounds, each one-sided bound, UTC-offset normalization, naive/invalid/reversed inputs, response shape, and 503 behavior.
- Verify a same-window request within 60 seconds does not call the builder again, a different window misses, and an expired entry recomputes. Control the clock in tests; do not wait in real time.

### Task 3.3: Run and review focused validation

- Run from the repository root, overriding the monorepo's incident-API-only import path: `.venv/bin/python -m pytest --override-ini=pythonpath=services/telemetry-api services/telemetry-api/tests/test_analysis.py services/telemetry-api/tests/test_report_endpoint.py -q`.
- Run the available syntax/import check for the touched Python files and verify OpenAPI exposes `GET /telemetry/report`.
- Review the diff to confirm only the planned service files and tests changed; do not alter approved telemetry documents or migrations.
- Confirm the implementation meets the original requirements: at least three independent metrics; SQL date/type filtering; UTC conversion before grouping; no metric-calculation loops; JSON-safe grouped outputs; default seven-day window; `{period, metrics}` response; 60-second same-window cache; technical/operational metrics only.

## Dependencies and External Prerequisites

- Read and follow `docs/telemetry/telemetry-plan.md` and `docs/telemetry/event-schemas.json`; the plan above records the specific operational scope and metric semantics needed for this report.
- Existing telemetry storage is Postgres `public.telemetry_events`; `tags` is JSONB. Relevant event fields include `timestamp`, `event_type`, and `tags`; `api_latency_recorded` defines `routeTemplate`, `method`, `httpStatus`, and `durationMs`.
- Report reads use the same `TELEMETRY_DATABASE_URL` pool as ingestion. The `telemetry_ingest` role must have SELECT on `event_type`, `timestamp`, and `tags`; the new migration supplies these grants.

## Task Status

| Task                                                      | Status                             |
| --------------------------------------------------------- | ---------------------------------- |
| Phase 1, Task 1.1: Add dependency and analysis module     | Complete                           |
| Phase 1, Task 1.2: Implement the three metrics            | Complete                           |
| Phase 1, Task 1.3: Enforce Pandas and serialization rules | Complete                           |
| Phase 1, Task 1.4: Configure report read access           | Complete locally; deploy migration |
| Phase 2, Task 2.1: Define date parameter behavior         | Complete                           |
| Phase 2, Task 2.2: Build and serve the report             | Complete                           |
| Phase 2, Task 2.3: Add the 60-second process-local cache  | Complete                           |
| Phase 3, Task 3.1: Create analysis tests                  | Complete                           |
| Phase 3, Task 3.2: Create endpoint and cache tests        | Complete                           |
| Phase 3, Task 3.3: Run and review focused validation      | Complete                           |
