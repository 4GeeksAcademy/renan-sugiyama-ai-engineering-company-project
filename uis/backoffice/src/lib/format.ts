const labels: Record<string, string> = {
  web_chat: "Web chat",
  technical_issue: "Technical issue",
  access_account_issue: "Access/account issue",
  billing_issue: "Billing issue",
  service_request: "Service request",
  information_request: "Information request",
  complaint: "Complaint",
  security_privacy_issue: "Security/privacy issue",
  in_progress: "In progress",
  pending_customer: "Pending customer",
  reopened: "Reopened",
  marketing_and_communications: "Marketing and Communications",
  sales_and_business_development: "Sales and Business Development",
  human_resources_internal: "Human Resources (Internal)",
  talent_selection_operations: "Talent Selection Operations",
  corporate_training: "Corporate Training",
  customer_support_outsourced: "Customer Support (outsourced service)",
  technology_and_infrastructure: "Technology and Infrastructure",
  executive_direction: "Executive Direction",
};

export const transitions: Record<string, string[]> = {
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

export const readable = (value: string) =>
  labels[value] ||
  value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export const formatDate = (value: string) =>
  new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));

export const isOverdue = (incident: {
  status: string;
  sla_target_at: string | null;
}) =>
  incident.sla_target_at !== null &&
  incident.status !== "closed" &&
  new Date(incident.sla_target_at) < new Date();
