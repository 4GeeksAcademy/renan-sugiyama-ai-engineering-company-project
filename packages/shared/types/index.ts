export type Id = string;

export interface BaseEntity {
  id: Id;
  createdAt?: string;
  updatedAt?: string;
}

export type IsoDateTime = string;

export const INTAKE_CHANNELS = ["phone", "email", "web_chat"] as const;
export type IntakeChannel = (typeof INTAKE_CHANNELS)[number];

export const INCIDENT_TYPES = [
  "technical_issue",
  "access_account_issue",
  "billing_issue",
  "service_request",
  "information_request",
  "complaint",
  "security_privacy_issue",
] as const;
export type IncidentType = (typeof INCIDENT_TYPES)[number];

export const INCIDENT_SEVERITIES = [
  "critical",
  "high",
  "medium",
  "low",
] as const;
export type IncidentSeverity = (typeof INCIDENT_SEVERITIES)[number];

export const INCIDENT_STATUSES = [
  "open",
  "in_progress",
  "pending_customer",
  "escalated",
  "resolved",
  "closed",
  "reopened",
] as const;
export type IncidentStatus = (typeof INCIDENT_STATUSES)[number];

export const RESPONSIBLE_AREAS = [
  "marketing_and_communications",
  "sales_and_business_development",
  "human_resources_internal",
  "talent_selection_operations",
  "corporate_training",
  "customer_support_outsourced",
  "technology_and_infrastructure",
  "executive_direction",
] as const;
export type ResponsibleArea = (typeof RESPONSIBLE_AREAS)[number];

export const INCIDENT_STATUS_TRANSITIONS: Readonly<
  Record<IncidentStatus, readonly IncidentStatus[]>
> = {
  open: ["in_progress", "escalated"],
  in_progress: ["open", "pending_customer", "escalated", "resolved"],
  pending_customer: ["in_progress", "resolved"],
  escalated: ["open", "in_progress", "resolved"],
  resolved: [
    "in_progress",
    "pending_customer",
    "escalated",
    "closed",
    "reopened",
  ],
  closed: ["reopened"],
  reopened: ["in_progress", "resolved"],
};

export function isValidIncidentStatusTransition(
  previousStatus: IncidentStatus,
  newStatus: IncidentStatus,
): boolean {
  return INCIDENT_STATUS_TRANSITIONS[previousStatus].includes(newStatus);
}

export interface Incident extends BaseEntity {
  title: string;
  description: string;
  channel: IntakeChannel;
  type: IncidentType;
  severity: IncidentSeverity;
  responsibleArea: ResponsibleArea;
  status: IncidentStatus;
  reporter: string;
  clientAccount?: string;
  slaTargetAt: IsoDateTime;
  resolvedAt?: IsoDateTime;
  closedAt?: IsoDateTime;
  createdBy: Id;
  updatedBy: Id;
}

export interface CreateIncidentRequest {
  title: string;
  description: string;
  channel: IntakeChannel;
  type: IncidentType;
  severity: IncidentSeverity;
  responsibleArea: ResponsibleArea;
  reporter: string;
  clientAccount?: string;
}

export interface UpdateIncidentRequest {
  title?: string;
  description?: string;
  channel?: IntakeChannel;
  type?: IncidentType;
  severity?: IncidentSeverity;
  reporter?: string;
  clientAccount?: string;
}

export interface AssignIncidentRequest {
  responsibleArea: ResponsibleArea;
  reason?: string;
}

export interface ChangeIncidentStatusRequest {
  status: IncidentStatus;
  reason?: string;
}

export type AuditEventType = "status_changed" | "responsible_area_changed";

export interface AuditEvent extends BaseEntity {
  incidentId: Id;
  eventType: AuditEventType;
  actorId: Id;
  occurredAt: IsoDateTime;
  previousValue: string;
  newValue: string;
  reason?: string;
  correlationId: string;
}

export interface StatusChangedAuditEvent extends AuditEvent {
  eventType: "status_changed";
  previousValue: IncidentStatus;
  newValue: IncidentStatus;
}

export interface ResponsibleAreaChangedAuditEvent extends AuditEvent {
  eventType: "responsible_area_changed";
  previousValue: ResponsibleArea;
  newValue: ResponsibleArea;
}

export type IncidentAuditEvent =
  | StatusChangedAuditEvent
  | ResponsibleAreaChangedAuditEvent;

export type IncidentSortField =
  | "createdAt"
  | "updatedAt"
  | "severity"
  | "status"
  | "responsibleArea";

export interface IncidentFilters {
  search?: string;
  status?: IncidentStatus;
  severity?: IncidentSeverity;
  responsibleArea?: ResponsibleArea;
}

export interface PageRequest {
  page: number;
  pageSize: number;
  sortBy?: IncidentSortField;
  sortDirection?: "asc" | "desc";
}

export interface IncidentListRequest extends PageRequest {
  filters?: IncidentFilters;
}

export interface PageResponse<T> {
  items: T[];
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

export interface IncidentListResponse extends PageResponse<Incident> {}

export interface IncidentDetailResponse {
  incident: Incident;
  auditHistory: IncidentAuditEvent[];
}

export interface OpenIncidentCountsBySeverity {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface IncidentSummaryResponse {
  openIncidentCountsBySeverity: OpenIncidentCountsBySeverity;
}

export interface CatalogsResponse {
  channels: readonly IntakeChannel[];
  types: readonly IncidentType[];
  severities: readonly IncidentSeverity[];
  statuses: readonly IncidentStatus[];
  responsibleAreas: readonly ResponsibleArea[];
}

export interface ApiError {
  code: string;
  message: string;
  correlationId: string;
}

export interface BackofficeActor {
  id: Id;
  role: "backoffice";
}
