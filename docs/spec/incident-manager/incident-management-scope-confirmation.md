# Incident Management Phase 1: Scope Confirmation

## Purpose

This document records the Phase 1 scope review for the Customer Support (outsourced service) incident manager. It is a decision log, not an implementation specification. The Phase 1 decisions have been approved by Nexova and can be used to begin Phase 2.

The English values below are approved display labels. API payloads, persistence, filters, and shared contracts use the stable codes documented in [`docs/incident-management-catalogs.md`](../docs/incident-management-catalogs.md), which also defines the initial Portuguese and Spanish frontend labels.

## Confirmed from the repository

The following values are supported by `CONTEXT.md` and the implementation plan:

### Intake channels

- `phone`
- `email`
- `web chat`

### Responsible areas

- Marketing and Communications
- Sales and Business Development
- Human Resources (Internal)
- Talent Selection Operations (core business)
- Corporate Training
- Customer Support (outsourced service)
- Technology and Infrastructure
- Executive Direction

The relevant operating team is Customer Support (outsourced service), managed by Roberto Diaz, with 30 agents. The committed SLA is 24 hours and the current average resolution time is 48 hours.

## Approved catalogs

The following controlled values are approved for use in shared contracts and persistence constraints:

### Type

- Technical issue
- Access/account issue
- Billing issue
- Service request
- Information request
- Complaint
- Security/privacy issue

### Severity

- Critical
- High
- Medium
- Low

### Status

- Open
- In progress
- Pending customer
- Escalated
- Resolved
- Closed
- Reopened

Priorities and categories remain intentionally undefined. They must not be added during implementation.

## Approved decisions

### Lifecycle transition matrix

The following transitions are approved:

- Open -> In progress
- Open -> Escalated
- In progress -> Pending customer
- In progress -> Escalated
- In progress -> Resolved
- Pending customer -> In progress
- Pending customer -> Resolved
- Escalated -> In progress
- Escalated -> Resolved
- Resolved -> Closed
- Resolved -> Reopened
- Closed -> Reopened
- Reopened -> In progress

The implementation must reject all transitions outside this matrix. Reopening a Closed incident requires an authorized backoffice user.

### Assignment and permissions

Any user with an assigned backoffice role can:

- create incidents;
- edit incident fields;
- assign or reassign the responsible area;
- change lifecycle status;
- reopen Resolved or Closed incidents;
- view client information and audit history;
- manage controlled catalogs.

The requirement that each incident has exactly one active responsible area is an approved domain constraint. Assigned backoffice users may assign and reassign the responsible area.

### Mandatory fields

The following minimum required fields for creation are approved:

- intake channel;
- title or short description;
- detailed description;
- type;
- severity;
- exactly one responsible area;
- reporter or source information;
- created-by user.

The initial status defaults to `Open` and is server-controlled. Client/account information is required when applicable.

### SLA calendar and escalation

The SLA applies only to incidents with `Critical` severity and is measured in 24 elapsed hours. High, Medium, and Low incidents have no SLA target. No separate business-hours calendar applies. The current 48-hour average is an operational baseline, not an additional catalog value or target rule.

### Retention and audit policy

The approved retention and audit rules are:

- incident records are retained for 1 month;
- audit events are retained for 1 year;
- legal or operational holds may be applied to any incident or audit event;
- any user with an assigned backoffice role may view audit history;
- client/account fields require no masking or additional protection.

Audit events are immutable, server-timestamped, and created for every status and responsible-area change.

## Canonical naming

The canonical responsible-area name is `Executive Direction`. Do not introduce `Executive Leadership` as an alias.

## Phase 1 gate

Phase 1 is complete. Phase 2 may implement the approved shared contracts, including the controlled catalogs, transition matrix, mandatory fields, role permissions, SLA measurement, retention rules, audit visibility, and canonical responsible-area names.
