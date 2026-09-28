export type Id = string;

export interface BaseEntity {
  id: Id;
  createdAt?: string;
  updatedAt?: string;
}

export * from "./inventory-manager";
export * from "./incident-manager";

export type IsoDateTime = string;

export interface PageResponse<T> {
  items: T[];
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
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
