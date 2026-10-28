export const TELEMETRY_SCHEMA_VERSION = "2.0.0";

export type TelemetryContext = {
  userId: string;
  sessionId: string;
  expiresAt: string;
  requestId: string;
};

let context: TelemetryContext | null = null;

export function setTelemetryContext(value: TelemetryContext | null): void {
  context = value ? { ...value } : null;
}

export function getTelemetryContext(): TelemetryContext | null {
  if (!context || Date.parse(context.expiresAt) <= Date.now()) return null;
  return context;
}
