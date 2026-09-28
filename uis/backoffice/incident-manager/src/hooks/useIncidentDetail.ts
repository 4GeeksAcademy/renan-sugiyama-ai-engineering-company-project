import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { IncidentDetailResponse } from "../types";

export function useIncidentDetail(incidentId: string | undefined) {
  return useQuery<IncidentDetailResponse>({
    queryKey: ["incident", incidentId],
    queryFn: () => api(`/incidents/${incidentId}`),
  });
}
