import { create } from "zustand";
import type { UiState } from "../types";

export const useUiStore = create<UiState>((set) => ({
  filters: { search: "", status: "", severity: "", responsible_area: "" },
  page: 1,
  toast: "",
  setFilter: (name, value) =>
    set((state) => ({ filters: { ...state.filters, [name]: value }, page: 1 })),
  clearFilters: () =>
    set({
      filters: { search: "", status: "", severity: "", responsible_area: "" },
      page: 1,
    }),
  setPage: (page) => set({ page }),
  showToast: (toast) => {
    set({ toast });
    window.setTimeout(() => set({ toast: "" }), 3500);
  },
}));
