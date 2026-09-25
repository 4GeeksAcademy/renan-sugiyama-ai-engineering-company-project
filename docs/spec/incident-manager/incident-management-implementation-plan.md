# Incident Management Implementation Plan

## 1. Purpose

Implement a traceable incident-management system for Nexova Solutions, focused on the **Customer Support (outsourced service)** operation.

The system must support incident creation, editing, listing, viewing, classification, assignment, lifecycle tracking, SLA visibility, and auditable history.

This is the implementation plan and status record for the incident-management slice. The approved local implementation is now present; the remaining work is production hardening, broader tests, deployment, and future AI capabilities.

## 2. Business Context

Nexova Solutions provides HR consulting, talent acquisition, outsourced customer support, and corporate training. The relevant department is **Customer Support (outsourced service)**, managed by Roberto Díaz with 30 agents.

Its clients operate in technology, retail, and finance. Incidents arrive through phone, email, and web chat. The committed SLA for Critical incidents is 24 hours, while the current average resolution time is 48 hours. Agents currently rely on experience and a shared Word document on Drive, and supervisors lack real-time workload and backlog visibility.

## 3. Controlled Catalogs

The channel catalog is defined by `CONTEXT.md` and must contain only:

- `phone`
- `email`
- `web chat`

Use these initial controlled values for the incident manager. They should be validated by Nexova before production use:

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

### Responsible area

The responsible-area catalog must use all departments defined in `CONTEXT.md`:

- Marketing and Communications
- Sales and Business Development
- Human Resources (Internal)
- Talent Selection Operations (core business)
- Corporate Training
- Customer Support (outsourced service)
- Technology and Infrastructure
- Executive Direction

Priorities and categories remain pending business decisions and must not be invented in the implementation.

## 4. Initial Scope

The first release must include:

1. Incident creation from phone, email, and web chat.
2. Required type and severity from the controlled catalogs.
3. Assignment to exactly one active responsible area.
4. Incident editing according to user permissions.
5. Incident listing with pagination, search, sorting, and filters by status, severity, and responsible area.
6. Incident detail viewing.
7. Lifecycle management from opening through closure.
8. Audit history for status and responsible-area changes.
9. An incident-detail view that exposes the audit history.
10. A summary showing open incident counts grouped by severity.
11. Basic SLA and backlog visibility.
12. Role-based access control.
13. Shared typed contracts and automated tests.

## 5. Domain Model

### Incident

Each incident should contain at least:

- `id`
- External or source reference, when available.
- Title or short description.
- Detailed description.
- Intake channel.
- Type.
- Severity.
- Responsible area.
- Current status.
- Reporter or source information.
- Client or account information, when applicable.
- Creation timestamp.
- Last-update timestamp.
- SLA target timestamp.
- Resolution timestamp, when applicable.
- Closure timestamp, when applicable.
- Created-by user.
- Updated-by user.

Type, severity, status, and responsible area must be references to controlled catalog values, not free text.

### Audit event

Every status change and responsible-area change must create an immutable audit event containing:

- Incident identifier.
- Event type.
- Author or actor identifier.
- Server-generated timestamp.
- Previous value.
- New value.
- Optional reason or comment.
- Correlation/request identifier.

Audit history must not be editable through normal application workflows.

## 6. Lifecycle

The minimum lifecycle is:

1. `Open`: incident is registered.
2. `In progress`: a responsible area is working on it.
3. `Pending customer`: progress is waiting for customer information, when applicable.
4. `Escalated`: the incident requires escalation, when applicable.
5. `Resolved`: a solution has been provided.
6. `Closed`: the incident is completed and closed.
7. `Reopened`: a closed or resolved incident requires additional work.

The API must reject invalid transitions. Every transition must record its author and timestamp. A closed incident may return to `Reopened` only through an authorized action.

## 7. Repository Architecture

Follow the existing monorepo boundaries and conventions:

- `packages/shared`: shared TypeScript incident, catalog, audit, API, pagination, and filtering contracts.
- `services`: centralized FastAPI backend for incident operations, persistence, authorization, SLA calculations, filtering, and audit events.
- `uis`: back-office registration, editing, listing, detail, audit, lifecycle, and summary views.
- `data`: only data pipelines, reporting extracts, evaluation, or later AI processing as needed.
- `docs`: approved catalog documentation, workflow rules, permissions, API behavior, and operating procedures.

Reuse the stack and patterns already established in the monorepo. Do not introduce a new library, package manager, or architectural pattern unless an existing project rule justifies it. Do not introduce microservices for the first release.

## 8. API Requirements

The centralized API must support:

- Create, retrieve, update, and list incidents.
- Register only the supported channels.
- Validate type, severity, responsible area, and status against their catalogs.
- Assign and reassign an incident.
- Change status through valid lifecycle transitions.
- Record audit events transactionally with status and assignment changes.
- Filter the incident list by status, severity, and responsible area.
- Return open incident counts grouped by severity.
- Retrieve the complete incident history.
- Enforce authenticated, role-based authorization.

Configuration endpoints should expose the active channel, type, severity, status, and responsible-area catalogs.

## 9. Back-Office Requirements

### Incident registration and editing

The form must include channel, title or summary, description, type, severity, responsible area, and initial status. Users may edit incident fields only according to their permissions.

### Incident list

The list must provide search, pagination, sorting, and filters for:

- Status.
- Severity.
- Responsible area.

It should show the current status, severity, responsible area, channel, SLA condition, creation time, and last-update time.

### Incident detail

The detail view must show the complete incident record, current status, severity, responsible area, SLA information, available actions, and the full audit history.

### Severity summary

Provide a view showing the number of open incidents for each severity. Selecting a severity should open the corresponding filtered incident list. Only incidents whose status is not `Closed` should be counted as open, unless Nexova approves a different rule.

## 10. Persistence, Security, and Integrity

The persistence layer must provide durable incident and audit records, referential integrity for catalogs, server-generated timestamps, indexes for list filters, and protection against audit deletion.

Status or responsible-area updates and their audit events must be committed atomically or through an equivalent consistency guarantee.

The system must use authenticated users, server-side authorization, protected client information, input validation, audit access controls, and retention rules approved by Nexova.

## 11. Implementation Phases

### Phase 1: Confirm scope

- Validate the proposed type, severity, and status values.
- Confirm valid lifecycle transitions.
- Confirm assignment permissions and routing rules for the eight departments.
- Define mandatory fields, SLA calendar, escalation rules, and retention policy.

### Phase 2: Shared contracts

- Extend `packages/shared` with incident, catalog, audit, filtering, and API contracts.
- Add contract tests.

### Phase 3: Backend and persistence

- Implement the centralized FastAPI incident module under `services`.
- Add persistence models and migrations.
- Implement CRUD, catalog validation, assignment, lifecycle transitions, authorization, and transactional audit events.
- Add API and persistence tests.

### Phase 4: Back office

- Implement registration, editing, listing, filtering, detail, audit history, lifecycle controls, and severity summary under `uis`.
- Add UI tests for the main workflow.

### Phase 5: SLA and pilot

- Implement SLA and backlog indicators.
- Validate the Critical-only 24-hour SLA against the 48-hour current average.
- Pilot with the Customer Support (outsourced service) team and collect operational feedback.

#### Local implementation status

The back office now exposes live operational summary metrics from the API:

- Open backlog count for incidents whose status is not `Closed`.
- Overdue open Critical incidents based on the elapsed 24-hour SLA target.
- Resolved-within-SLA percentage from incidents with a resolution timestamp.
- Average elapsed resolution time from resolved incidents.
- Existing open counts grouped by severity remain available as filterable queue cards.

The pilot validation remains an operational task. Nexova must compare the local metrics with the Customer Support team's records, confirm the 48-hour average-resolution baseline, and collect feedback on backlog and SLA usefulness before production hardening.

### Phase 6: Future capabilities

After the core workflow is stable, consider the centralized knowledge base, semantic search, RAG chatbot, 40% automated-resolution goal, real-time support dashboard, and sentiment analysis.

## 12. Acceptance Criteria

The first release is acceptable only if:

1. Incidents can be created from phone, email, and web chat.
2. Every incident requires a controlled type and severity.
3. Every incident is assigned to exactly one responsible area from the eight departments.
4. Incidents can be edited according to permissions.
5. Incidents can be listed and filtered by status, severity, and responsible area.
6. Incidents can be viewed with their complete audit history.
7. Incidents can move from `Open` through resolution to `Closed` using valid transitions.
8. Invalid lifecycle transitions are rejected.
9. Every status change records author, timestamp, previous value, and new value.
10. Every responsible-area change records author, timestamp, previous value, and new value.
11. Open incident counts are shown grouped by severity.
12. Unauthorized users cannot perform restricted actions.
13. API and UI tests cover creation, editing, listing, viewing, lifecycle, filtering, summary, and audit behavior.

## 13. Project State and Constraints

The approved local incident-management slice is implemented across:

- `packages/shared/` for TypeScript contracts and type tests;
- `services/api/` for the FastAPI application, SQLite persistence, migrations, catalogs, lifecycle rules, audit events, and contract tests;
- `uis/backoffice/` for the Vite React queue, registration, detail, editing, lifecycle, audit, filtering, and summary workflows;
- `docs/incident-management-catalogs.md` for stable catalog codes and labels.

The repository does not yet include a production identity provider, root workspace runner, Docker Compose setup, deployed infrastructure, comprehensive persistence/API tests, or complete UI workflow tests. AI agents, MCP servers, data pipelines, and workflow automation remain future extension areas.

The local API uses `X-Backoffice-User` authentication backed by the SQLite `backoffice_users` table. The default local UI user is `local-user`, which must be seeded before using protected endpoints.

The implementation follows the approved catalogs, lifecycle transitions, assignment rules, mandatory fields, Critical-only 24-hour elapsed-time SLA, and audit requirements recorded in the scope confirmation. Future changes must preserve those controlled values and transition constraints unless the business decision log is updated.
