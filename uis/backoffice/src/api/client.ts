const API_BASE = window.INCIDENT_API_URL || "http://localhost:8000";
const USER_ID = window.INCIDENT_USER_ID || "local-user";

export async function api(
  path: string,
  options: RequestInit = {},
): Promise<any> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Backoffice-User": USER_ID,
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}
