type TelemetryEvent = {
  event_type: string;
  properties: Record<string, unknown>;
};

const TELEMETRY_ENDPOINT = process.env.NEXT_PUBLIC_TELEMETRY_ENDPOINT;
const MAX_BATCH_SIZE = 20;
const FLUSH_INTERVAL_MS = 10_000;
const MAX_RETRIES = 3;
const RETRY_BASE_DELAY_MS = 1_000;

const eventQueue: TelemetryEvent[] = [];
let flushTimer: ReturnType<typeof setTimeout> | undefined;
let flushInProgress: Promise<void> | undefined;

export function track(
  eventType: string,
  properties: Record<string, unknown>,
): void {
  enqueueEvent({ event_type: eventType, properties });
}

function enqueueEvent(event: TelemetryEvent): void {
  if (!TELEMETRY_ENDPOINT) return;

  eventQueue.push(event);
  if (eventQueue.length >= MAX_BATCH_SIZE) {
    void flushQueue();
  } else {
    scheduleFlush();
  }
}

function scheduleFlush(): void {
  if (flushTimer !== undefined) return;

  flushTimer = setTimeout(() => {
    flushTimer = undefined;
    void flushQueue();
  }, FLUSH_INTERVAL_MS);
}

function clearFlushTimer(): void {
  if (flushTimer === undefined) return;

  clearTimeout(flushTimer);
  flushTimer = undefined;
}

function delay(milliseconds: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function sendBatchWithRetry(batch: TelemetryEvent[]): Promise<void> {
  if (!TELEMETRY_ENDPOINT) return;

  for (let retry = 0; retry <= MAX_RETRIES; retry += 1) {
    try {
      const response = await fetch(TELEMETRY_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events: batch }),
      });

      if (!response.ok)
        throw new Error(`Telemetry request failed: ${response.status}`);
      return;
    } catch {
      if (retry === MAX_RETRIES) return;
      await delay(RETRY_BASE_DELAY_MS * 2 ** retry);
    }
  }
}

async function flushQueue(): Promise<void> {
  clearFlushTimer();
  if (flushInProgress) return flushInProgress;
  if (eventQueue.length === 0 || !TELEMETRY_ENDPOINT) return;

  const batch = eventQueue.splice(0, MAX_BATCH_SIZE);
  flushInProgress = sendBatchWithRetry(batch).finally(() => {
    flushInProgress = undefined;

    if (eventQueue.length >= MAX_BATCH_SIZE) {
      void flushQueue();
    } else if (eventQueue.length > 0) {
      scheduleFlush();
    }
  });

  await flushInProgress;
}

function flushWithBeacon(): void {
  if (eventQueue.length === 0 || !TELEMETRY_ENDPOINT) return;
  clearFlushTimer();

  if (
    typeof navigator === "undefined" ||
    typeof navigator.sendBeacon !== "function"
  ) {
    void flushQueue();
    return;
  }

  while (eventQueue.length > 0) {
    const batch = eventQueue.slice(0, MAX_BATCH_SIZE);
    const body = new Blob([JSON.stringify({ events: batch })], {
      type: "application/json",
    });

    if (!navigator.sendBeacon(TELEMETRY_ENDPOINT, body)) {
      void flushQueue();
      return;
    }

    eventQueue.splice(0, batch.length);
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") flushWithBeacon();
  });
}
