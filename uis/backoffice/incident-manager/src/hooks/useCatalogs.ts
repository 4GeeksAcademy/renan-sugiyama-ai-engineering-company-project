import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Catalogs } from "../types";

export function useCatalogs() {
  return useQuery<Catalogs>({
    queryKey: ["catalogs"],
    queryFn: () => api("/catalogs"),
  });
}
