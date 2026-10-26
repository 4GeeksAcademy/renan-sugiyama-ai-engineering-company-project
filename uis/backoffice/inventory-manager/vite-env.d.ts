interface Window {
  INVENTORY_API_URL?: string;
  INVENTORY_USER_ID?: string;
}

declare const process: { env: Record<string, string | undefined> };
