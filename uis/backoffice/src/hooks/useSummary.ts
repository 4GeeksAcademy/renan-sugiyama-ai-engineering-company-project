import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Summary } from "../types";

export function useSummary() {
  return useQuery<Summary>({
    queryKey: ["summary"],
    queryFn: () => api("/summary"),
  });
}
