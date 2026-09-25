import {
  INCIDENT_SEVERITIES,
  INCIDENT_STATUS_TRANSITIONS,
  INCIDENT_STATUSES,
  INTAKE_CHANNELS,
  RESPONSIBLE_AREAS,
  isValidIncidentStatusTransition,
  type CatalogsResponse,
  type CreateIncidentRequest,
  type IncidentAuditEvent,
} from "./index";

const catalogs: CatalogsResponse = {
  channels: INTAKE_CHANNELS,
  types: [
    "technical_issue",
    "access_account_issue",
    "billing_issue",
    "service_request",
    "information_request",
    "complaint",
    "security_privacy_issue",
  ],
  severities: INCIDENT_SEVERITIES,
  statuses: INCIDENT_STATUSES,
  responsibleAreas: RESPONSIBLE_AREAS,
};

const creationRequest: CreateIncidentRequest = {
  title: "Cannot access account",
  description: "The customer cannot sign in.",
  channel: "web_chat",
  type: "access_account_issue",
  severity: "high",
  responsibleArea: "customer_support_outsourced",
  reporter: "customer@example.com",
};

const statusAuditEvent: IncidentAuditEvent = {
  id: "audit-1",
  incidentId: "incident-1",
  eventType: "status_changed",
  actorId: "user-1",
  occurredAt: "2026-09-25T12:00:00Z",
  previousValue: "open",
  newValue: "in_progress",
  correlationId: "request-1",
};

function assertContract(condition: boolean): void {
  if (!condition) {
    throw new Error("Shared incident contract assertion failed");
  }
}

assertContract(catalogs.channels.length === 3);
assertContract(!("status" in creationRequest));
assertContract(statusAuditEvent.eventType === "status_changed");
assertContract(isValidIncidentStatusTransition("closed", "reopened"));
assertContract(!isValidIncidentStatusTransition("open", "closed"));
assertContract(INCIDENT_STATUS_TRANSITIONS.closed.length === 1);