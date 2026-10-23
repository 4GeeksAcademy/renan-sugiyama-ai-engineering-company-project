"use client";

import { useLayoutEffect } from "react";
import {
  setTelemetryContext,
  type TelemetryContext,
} from "@nexova/telemetry/context";

export function TelemetrySession({ context }: { context: TelemetryContext }) {
  const { userId, sessionId, expiresAt, requestId } = context;

  useLayoutEffect(() => {
    setTelemetryContext({ userId, sessionId, expiresAt, requestId });
    return () => setTelemetryContext(null);
  }, [userId, sessionId, expiresAt, requestId]);

  return null;
}
