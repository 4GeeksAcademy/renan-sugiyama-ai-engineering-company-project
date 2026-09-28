import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import { useUiStore } from "../store/uiStore";
import type { ActionRequest, IncidentPayload } from "../types";

export function useCreateIncident(onSuccess: () => void) {
  const queryClient = useQueryClient();
  const showToast = useUiStore((state) => state.showToast);
  return useMutation<unknown, Error, IncidentPayload>({
    mutationFn: (payload) =>
      api("/incidents", { method: "POST", body: JSON.stringify(payload) }),
    onSuccess: () => {
      queryClient.invalidateQueries();
      showToast("Incident created");
      onSuccess();
    },
    onError: (error) => showToast(error.message),
  });
}

export function useIncidentAction(incidentId: string | undefined) {
  const queryClient = useQueryClient();
  const showToast = useUiStore((state) => state.showToast);
  return useMutation<unknown, Error, ActionRequest>({
    mutationFn: ({ path, payload }) =>
      api(path, { method: "POST", body: JSON.stringify(payload) }),
    onSuccess: () => {
      queryClient.invalidateQueries();
      showToast("Incident updated");
    },
    onError: (mutationError) => showToast(mutationError.message),
  });
}

export function useUpdateIncident(incidentId: string | undefined) {
  const queryClient = useQueryClient();
  const showToast = useUiStore((state) => state.showToast);
  return useMutation<unknown, Error, IncidentPayload>({
    mutationFn: (payload) =>
      api(`/incidents/${incidentId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incident", incidentId] });
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      showToast("Incident updated");
    },
    onError: (mutationError) => showToast(mutationError.message),
  });
}
