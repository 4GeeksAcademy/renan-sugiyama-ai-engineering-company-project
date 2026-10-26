import { randomUUID } from "node:crypto";
import App, { type DashboardData } from "../App";
import { redirect } from "next/navigation";
import { TelemetrySession } from "../components/TelemetrySession";
import { getSession } from "../lib/auth";

export default async function Page() {
  const session = await getSession();
  if (!session) redirect("/login");

  const requestId = randomUUID();
  const telemetrySession = (
    <TelemetrySession
      context={{
        userId: session.userId,
        sessionId: session.sessionId,
        expiresAt: session.expiresAt,
        requestId,
      }}
    />
  );

  let data: DashboardData;

  try {
    const apiUrl = process.env.DASHBOARD_API_URL ?? "http://127.0.0.1:8002";
    const response = await fetch(`${apiUrl.replace(/\/$/, "")}/dashboard`, {
      cache: "no-store",
      headers: { "X-Request-ID": requestId },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      throw new Error(`Dashboard API returned ${response.status}`);
    }

    data = await response.json();
  } catch {
    return (
      <>
        {telemetrySession}
        <App error="Dashboard data is unavailable. Please try again later." />
      </>
    );
  }

  return (
    <>
      {telemetrySession}
      <App data={data} />
    </>
  );
}
