import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { setTelemetryContext } from "@nexova/telemetry/context";
import { App } from "./App";
import "./styles.css";

const SESSION_KEY = "telemetry_session_id";
const sessionId = sessionStorage.getItem(SESSION_KEY) ?? crypto.randomUUID();
sessionStorage.setItem(SESSION_KEY, sessionId);
setTelemetryContext({
  userId: window.INVENTORY_USER_ID || "local-user",
  sessionId,
  expiresAt: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
  requestId: crypto.randomUUID(),
});

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </QueryClientProvider>,
);
