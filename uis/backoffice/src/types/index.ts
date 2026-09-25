import type { ChangeEvent } from "react";

export type Catalogs = {
  channels: string[];
  types: string[];
  severities: string[];
  statuses: string[];
  responsible_areas: string[];
};

export type Incident = {
  id: string;
  title: string;
  description: string;
  channel: string;
  type: string;
  severity: string;
  responsible_area: string;
  status: string;
  reporter: string;
  client_account?: string;
  sla_target_at: string | null;
  updated_at: string;
};

export type IncidentPayload = Omit<
  Incident,
  "id" | "sla_target_at" | "updated_at" | "status"
>;

export type AuditEvent = {
  id: string;
  event_type: string;
  previous_value: string;
  new_value: string;
  occurred_at: string;
  actor_id: string;
  reason?: string;
};

export type IncidentDetailResponse = {
  incident: Incident;
  audit_history: AuditEvent[];
};

export type IncidentListResponse = {
  items: Incident[];
  page: number;
  total_items: number;
  total_pages: number;
};

export type Summary = {
  open_incident_counts_by_severity: Record<string, number>;
  open_backlog_count: number;
  overdue_open_incident_count: number;
  sla_hours: number;
  average_resolution_hours: number | null;
  resolved_within_sla_percent: number | null;
};

export type ActionRequest = { path: string; payload: Record<string, string> };

export type Filters = {
  search: string;
  status: string;
  severity: string;
  responsible_area: string;
};

export type FilterName = keyof Filters;

export type UiState = {
  filters: Filters;
  page: number;
  toast: string;
  setFilter: (name: FilterName, value: string) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  showToast: (toast: string) => void;
};

export type ChangeHandler = (
  event: ChangeEvent<
    HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
  >,
) => void;

export type FieldProps = {
  label: string;
  name: string;
  value: string;
  onChange: ChangeHandler;
  required?: boolean;
  textarea?: boolean;
  full?: boolean;
};
