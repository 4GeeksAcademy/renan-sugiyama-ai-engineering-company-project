import App, { type DashboardData } from "../App";

export default async function Page() {
  let data: DashboardData;

  try {
    const apiUrl = process.env.DASHBOARD_API_URL ?? "http://127.0.0.1:8002";
    const response = await fetch(`${apiUrl.replace(/\/$/, "")}/dashboard`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      throw new Error(`Dashboard API returned ${response.status}`);
    }

    data = await response.json();
  } catch {
    return <App error="Dashboard data is unavailable. Please try again later." />;
  }

  return <App data={data} />;
}