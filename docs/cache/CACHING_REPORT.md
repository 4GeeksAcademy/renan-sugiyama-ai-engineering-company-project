# Caching and Loading Decisions

## Frontend Decisions

### Lazy-loaded inventory workflows

The inventory manager keeps the item list as its eagerly loaded default view. `InventoryItemFormPage` (create/edit), `InventoryItemDetailPage`, and `InventoryMovementPage` are separate `React.lazy` route modules wrapped in `Suspense` in `uis/backoffice/inventory-manager/src/App.tsx`. They are needed only after a user navigates to those workflows, so deferring them avoids downloading and parsing their code for users who only view the item list.

The production build emitted separate chunks for these workflows:

| Chunk                 | Built size | Gzip size |
| --------------------- | ---------: | --------: |
| Item detail           |    2.71 kB |   0.94 kB |
| Item create/edit form |    2.98 kB |   1.17 kB |
| Movement form         |    6.76 kB |   2.26 kB |

These are measured output sizes, not a before/after benchmark. They confirm that the route code is split; the expected initial-load benefit is avoiding transfer and parse of unused chunks. The build did not measure user-perceived latency or prove an improvement to Core Web Vitals.

### Memoized inventory lookup

`InventoryMovementPage` memoizes `selectedItem`, found by searching the complete inventory list for `itemId`. The list endpoint is unpaginated, and changes to quantity, reason, date, and other form state cause rerenders. With `inventoryItems` and `itemId` as dependencies, the linear search is skipped during those rerenders and recalculated when the list or selected ID changes.

The benefit is estimated rather than runtime-measured: it avoids repeat O(n) scans during unrelated form updates, with savings increasing as the inventory list grows. No benchmark was collected, and for a very small list the absolute savings may be negligible; the calculation was selected because it scales with list size and repeats across interactive renders, unlike simple formatting or boolean checks.

## Backend Decisions

Both caches are in-memory and process-local. Responses are copied when stored and returned, list cache keys include every query parameter, and both caches have bounded entry counts.

| Cached endpoint  | Operation cost                                                                                                                                                     | Call frequency estimate                                                                   |        TTL | Invalidation                                                                                                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- | ---------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /incidents` | Medium-high: performs a count query and a filtered, sorted, paginated query, then maps rows to response models. Search and filters can increase the database work. | High: the incident queue requests it on view and again when filters or pagination change. | 10 seconds | Clear all incident read caches after successful create, update, assignment, and status-change writes. The TTL also bounds staleness if data changes outside these handlers. |
| `GET /summary`   | High: runs two aggregate queries over the incidents table to calculate backlog, severity, SLA, and resolution metrics.                                             | High: requested alongside the incident queue summary cards.                               |  5 seconds | Clear all incident read caches after successful create, update, assignment, and status-change writes. TTL bounds staleness for time-dependent overdue counts.               |

### Freshness tradeoff

The summary cache uses a 5-second TTL. An overdue count can become stale for up to five seconds because the metric can change as time passes even when no incident is written. This short window is acceptable for operational overview cards: successful application writes invalidate immediately, while the TTL keeps a clock-driven metric current without rerunning full-table aggregates on every queue view. The list uses a 10-second TTL because its values change only through writes, which also trigger invalidation; the longer fallback window reduces repeated query work while keeping out-of-band changes bounded.

Because these caches are process-local, invalidation in one worker does not clear another worker's cache. TTL limits that cross-worker staleness, but a multi-worker deployment needing immediate cross-process consistency should use a shared cache or database-backed invalidation instead.

## Considered but Not Cached

`GET /catalogs` was considered but not cached. Its values are constants loaded from code, so they are stable and frequently reusable, but constructing the response is cheap and caching would save little. `GET /inventory/items/below-reorder-point` has more expensive stock aggregation, but no current frontend consumer was found; its observed call frequency is therefore low or unknown. Caching it now would add invalidation complexity without demonstrated repeat-read benefit.

Telemetry ingestion and authentication responses are also intentionally uncached: telemetry requests have side effects, and login/logout responses are session-specific and security-sensitive.

## Validation

The incident API contract test passed (`1 passed`). The inventory manager passed `npm run typecheck` and `npm run build`; the build output above confirms separate workflow chunks. No runtime latency benchmark was run, so frontend and backend performance benefits beyond the emitted chunk sizes remain estimates.
