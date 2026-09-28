import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Filters, IncidentListResponse } from "../types";

export function useIncidents(filters: Filters, page: number) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: "10",
    sort_by: "updated_at",
    sort_direction: "desc",
  });
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  return useQuery<IncidentListResponse>({
    queryKey: ["incidents", params.toString()],
    queryFn: () => api(`/incidents?${params}`),
  });
}
