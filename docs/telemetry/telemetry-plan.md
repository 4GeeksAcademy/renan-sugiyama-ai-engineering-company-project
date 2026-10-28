# Telemetry Processing Plan

This plan assigns a processing mode to every event in [event-schemas.json](event-schemas.json). The choice is based on the urgency of the decision the event supports, not implementation preference.

## Processing Modes

- **Stream:** Process continuously, with operational signals available within about one minute. Use for decisions that lose value if delayed: intervening with a customer, preventing a stockout, responding to a security or service incident, or maintaining a live operational view. Alert on meaningful conditions or aggregates, not on every individual event.
- **Batch:** Accumulate and process periodically. Use when the event supports trend measurement, reporting, or process improvement and waiting for the next scheduled update does not materially delay an operational response. Daily is the default; use weekly or monthly rollups where stated.

## Event Decisions

| `event_type`                           | Mode                                                          | Decision and urgency rationale                                                                                                                                                                                                    |
| -------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `website_visit_recorded`               | Batch, daily                                                  | Supports marketing traffic and source analysis. Reallocating marketing effort does not require action on each individual visit.                                                                                                   |
| `marketing_conversion_completed`       | Batch, daily                                                  | Feeds conversion-rate and campaign-performance reviews. Daily attribution is timely enough for campaign decisions; a single conversion does not require immediate intervention.                                                   |
| `sales_crm_coverage_snapshot_recorded` | Batch, weekly                                                 | Feeds the CRM adoption baseline and coaching decisions. Team-level coverage trends are reviewed periodically; a single rep's update does not warrant a real-time operational alert.                                               |
| `employee_departure_recorded`          | Batch, monthly turnover rollup                                | Supports turnover analysis and workforce planning, which are trend decisions rather than minute-to-minute actions. Any access revocation or offboarding workflow must use a separate event and run immediately.                   |
| `workforce_snapshot_recorded`          | Batch, daily collection with monthly rollup                   | Supplies the headcount denominator for turnover and absenteeism. These rates are management indicators, so a daily snapshot and periodic rollup are sufficient.                                                                   |
| `employee_absence_recorded`            | Stream to authorized staffing workflows; batch for HR metrics | Operations may need to reassign work or cover a shift promptly when an absence affects staffing. Restrict the real-time feed to authorized staffing users; use aggregated batches for absenteeism reporting.                      |
| `internal_requisition_opened`          | Batch, daily                                                  | Starts the time-to-fill measurement window. The KPI is used for recruiting capacity and process review, not an urgent per-requisition alert. Any separate recruiting task assignment can be handled by its workflow.              |
| `internal_role_filled`                 | Batch, daily with weekly/monthly rollup                       | Completes the time-to-fill measurement. Hiring efficiency is assessed as a trend, so immediate processing does not change the decision.                                                                                           |
| `support_ticket_resolved`              | Stream                                                        | Supervisors and account teams need current resolution and SLA status to manage service delivery and respond to client concerns. A delayed update can leave the operational dashboard and SLA view stale.                          |
| `support_queue_snapshot_recorded`      | Stream                                                        | Supports live workload, backlog, and staffing decisions. Supervisors need to reroute or rebalance work while the queue is changing, not after a reporting interval.                                                               |
| `support_query_closed`                 | Stream                                                        | Tracks chatbot resolution against the 40% target. A sustained drop can increase human queue load and threaten the 24-hour SLA, so operators should detect it soon enough to intervene.                                            |
| `support_dissatisfaction_detected`     | Stream                                                        | The intended action is to contact or otherwise assist an at-risk client before escalation. Waiting for a batch could erase that opportunity.                                                                                      |
| `support_ticket_escalated`             | Stream                                                        | An escalation requires timely supervisor or specialist attention. Delayed visibility prolongs an already critical customer issue.                                                                                                 |
| `department_kpi_snapshot_recorded`     | Stream                                                        | The briefing calls for a unified executive dashboard with real-time KPIs. Continuous processing keeps the leadership view current enough to support timely decisions.                                                             |
| `kpi_threshold_triggered`              | Stream                                                        | Strategic threshold alerts are actionable only while there is still time to respond. Process them as soon as the threshold condition is detected.                                                                                 |
| `user_authentication_denied`           | Stream, with alert aggregation                                | Security teams need to spot patterns of repeated or coordinated denials quickly. Stream the signals, but alert on suspicious patterns rather than each isolated denial to avoid treating normal mistakes as incidents.            |
| `stock_movement_validation_failed`     | Batch, daily                                                  | The API already rejects invalid input in the request-response path. Telemetry is for finding recurring validation problems and improving forms or guidance; an individual failure usually needs no separate operational response. |
| `direct_stock_edit_rejected`           | Batch, daily                                                  | The system immediately rejects direct edits to derived stock. Reviewing attempts periodically can inform training or UX changes; only a separate high-risk abuse rule would justify an immediate alert.                           |
| `outbound_stock_blocked`               | Stream                                                        | The operator needs immediate feedback that the requested outbound movement cannot proceed, and may need to choose a smaller quantity, replenish stock, or reconcile the ledger.                                                   |
| `stock_movement_recorded`              | Stream                                                        | Other inventory users and downstream operations need the updated stock position promptly. Immediate processing also enables timely threshold evaluation and prevents decisions based on stale availability.                       |
| `stock_threshold_triggered`            | Stream                                                        | Falling below the reorder point creates a replenishment decision. Delaying detection increases stockout risk; emit on the crossing, not on every subsequent read below the threshold.                                             |
| `stock_movement_correction_recorded`   | Stream                                                        | A correction changes the movement ledger and derived stock. Update availability and reevaluate reorder thresholds promptly so operators do not act on an incorrect balance.                                                       |
| `api_latency_recorded`                 | Stream, using rolling aggregates                              | Rapidly rising latency can impair inventory or support operations before users report a failure. Continuously evaluate rolling latency indicators and alert only when meaningful thresholds are breached.                         |
| `api_request_failed`                   | Stream, with severity filtering                               | Production failures can block user workflows and require prompt diagnosis. Stream failures for rapid detection; alert on server-side or dependency failures, while ordinary client validation errors should not page responders.  |

## Operational Notes

- Stream delivery does not imply that every event creates an alert. Use aggregation and severity rules so alerts represent decisions that need action.
- Batch schedules should match the decision cadence: daily for operational KPI refreshes, weekly for CRM adoption review, and monthly for workforce trend reporting.
- Sensitive absence and HR data must stay limited to authorized destinations. The stream/batch choice does not relax the field allowlists and sanitization rules in the event schema.
- The inventory API currently records stock movements rather than explicit inbound or outbound order entities. The inventory event decisions therefore apply to movement events; an order workflow should add order-level events if that entity is introduced.

## Throttling and Debouncing

Throttling limits how often a replaceable update or notification is emitted. Debouncing waits for a quiet interval before emitting the latest update. Debouncing is not appropriate for events where waiting could delay an operational decision.

- Deduplicate retries by `eventId` for all event types. This is idempotency, not rate limiting; distinct events must remain distinct.
- Never throttle or debounce stock movements, corrections, threshold crossings, blocked outbounds, ticket resolutions, escalations, dissatisfaction detections, absence records used for staffing, or authentication-denial audit events. Each can represent a distinct state change or intervention opportunity.
- `support_queue_snapshot_recorded`: throttle replaceable snapshots to at most one published snapshot per queue every 30 seconds, retaining the latest state in each interval. A threshold crossing must emit `kpi_threshold_triggered` immediately and must not wait for the snapshot interval.
- `api_latency_recorded`: do not debounce or discard individual measurements. Continuously aggregate them into one-minute route/method windows for latency decisions; alert on a breached rolling indicator, not on each slow request.
- `api_request_failed` and `user_authentication_denied`: retain each event, but throttle duplicate notifications to one summary per route and registered error/reason category per five minutes. Send an alert immediately if severity escalates; do not suppress the underlying events.
- `support_query_closed`: retain every outcome and calculate the automation rate in rolling 15-minute windows. Alert only when the window has enough eligible queries to make the rate actionable; do not debounce query outcomes. Configure the minimum count with support operations.
- `website_visit_recorded` and `marketing_conversion_completed`: do not throttle or debounce distinct visits or conversions. Their batch processing aggregates the records without losing individual conversion attribution.
- `stock_movement_validation_failed` and `direct_stock_edit_rejected`: retain distinct events and aggregate them in the planned daily review. The API response already handles the individual rejection; telemetry does not need to delay or replace it.
- Other low-frequency business events use event-ID deduplication only. Do not apply a generic debounce across state-change events.

Notification cooldowns apply only to duplicate alerts, never to the event stream or audit record. Any event that crosses a new severity level bypasses the cooldown.

## Risks and Exclusions

### Considered but excluded events

| Candidate event                                          | Reason for exclusion                                                                                                                                                                                      |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inventory_item_viewed` or `inventory_list_opened`       | A read does not indicate a stock or fulfillment decision. These events would be frequent and add volume without a clear action; API latency monitoring already covers service responsiveness.             |
| `inventory_order_created` or `inventory_order_fulfilled` | The current inventory API has movement records, not an order entity or lifecycle. Emitting order events would imply data and guarantees the system does not have. Revisit if an order workflow is added.  |
| `stock_level_read` or `below_reorder_point_listed`       | A read of an item already below its threshold is not a new activation. Logging reads would repeat the same condition; retain the crossing-based `stock_threshold_triggered` event instead.                |
| `form_field_changed`, keystroke, or navigation events    | No agreed business decision depends on these interactions. They are high-volume and can unintentionally capture typed personal or customer data.                                                          |
| `user_authentication_succeeded`                          | Successful access is not needed for the current denial-pattern investigation or business metrics. It would create a high-volume identity trail; add only if a defined access-review decision requires it. |

### Data not collected

- **Credentials and device identifiers:** Never collect passwords, auth headers, access or refresh tokens, raw usernames for unknown users, IP addresses, or browser/device fingerprints. Use pseudonymous envelope IDs and route templates.
- **Customer or employee content:** Never collect ticket/chat transcripts, customer messages, bot prompts or responses, CRM notes, form values, free-text movement/correction reasons, or arbitrary request/response bodies. Use approved categories and error codes only.
- **Direct identifiers and sensitive HR details:** Do not emit employee, candidate, or customer names, emails, phone numbers, CV contents, diagnoses, or medical notes. Use keyed pseudonymous IDs where event-level correlation is necessary; use aggregates for reporting and suppress small cohorts that could reveal an individual.
- **Unbounded diagnostic detail:** Do not collect raw exception messages, stack traces, full URLs, query strings, or referrer URLs. These can contain secrets or personal data and increase storage and indexing cost; use registered error codes, route templates, and bounded labels.
- **Per-interaction noise:** Do not collect every item read, refresh, keystroke, or field edit. These events have no defined decision value and can multiply ingestion and retention costs. Use the documented snapshots, stream aggregates, and batch rollups instead.

### Reserved event metadata

- `value` and `message` are reserved properties, not top-level envelope fields. The backend stores them in nullable columns and excludes them from JSONB `tags`; omitted or null values remain SQL `NULL`.
- Only `stock_movement_validation_failed`, `outbound_stock_blocked`, `stock_movement_recorded`, and `api_latency_recorded` may provide a numeric `value`. Use the attempted quantity, requested quantity, signed stock delta, and `durationMs`, respectively. Other event types must omit `value`.
- All error-level events require a nonempty `message` of at most 500 characters from the event schema's registered sanitized summaries. Non-error events may omit `message` or set it to null. Never send raw exceptions, response details, credentials, personal/customer content, or arbitrary free text.
- The required error summaries make this event contract version `2.0.0`; clients emitting error-level events must use the new contract.

### Risks and safeguards

- **Re-identification:** Pseudonymous IDs remain linkable. Keep the mapping separately protected, limit access and retention, and avoid exposing event-level identifiers in dashboards or metric labels.
- **Sensitive inference:** Absence and sentiment events can reveal sensitive information even without message text. Limit them to the authorized staffing or support workflows, retain only what is needed for the stated decision, and do not use sentiment alone for punitive decisions.
- **Small-group disclosure:** Department-level HR counts may identify individuals in small teams. Apply minimum cohort-size suppression before reporting.
- **Alert fatigue and event cost:** High-volume latency, authentication, and failure signals can create noisy alerts and expensive indexes. Preserve event records where specified, aggregate for decisions, and throttle duplicate notifications rather than dropping distinct audit or operational events.
- **False threshold or duplicate events:** Emit stock threshold events only on a genuine crossing; deduplicate retries by `eventId`. Monitor duplicate rates and incorrect threshold alerts because they can prompt unnecessary replenishment.
- **Unimplemented instrumentation:** This document and the schema define the intended contract; they do not prove that emitters, access controls, retention limits, or suppression rules are implemented. Verify those controls before using the events for operational or personnel decisions.
