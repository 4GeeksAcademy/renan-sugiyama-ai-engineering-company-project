import { Link, Routes, Route, useNavigate } from "react-router-dom";
import { queryClient } from "../api/queryClient";
import { useUiStore } from "../store/uiStore";
import { IncidentQueuePage } from "../pages/IncidentQueuePage";
import { IncidentFormPage } from "../pages/IncidentFormPage";
import { IncidentDetailPage } from "../pages/IncidentDetailPage";

export function AppShell() {
  const navigate = useNavigate();
  const showToast = useUiStore((state) => state.showToast);
  const toast = useUiStore((state) => state.toast);
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">N</span>
          <span>
            Nexova <strong>ops</strong>
          </span>
        </div>
        <p className="eyebrow">Customer support</p>
        <nav aria-label="Primary navigation">
          <Link className="nav-item active" to="/">
            <span className="nav-icon">▦</span> Incidents
          </Link>
          <button
            className="nav-item"
            type="button"
            onClick={() => {
              queryClient.invalidateQueries();
              showToast("Queue refreshed");
            }}
          >
            <span className="nav-icon">↻</span> Refresh data
          </button>
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Operations online</span>
          <small>24h Critical SLA</small>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Operations workspace</p>
            <h1>Incident control room</h1>
          </div>
          <div className="topbar-actions">
            <span className="user-chip">Local operator</span>
            <button
              className="button button-primary"
              type="button"
              onClick={() => navigate("/incidents/new")}
            >
              + New incident
            </button>
          </div>
        </header>
        <Routes>
          <Route path="/" element={<IncidentQueuePage />} />
          <Route path="/incidents/new" element={<IncidentFormPage />} />
          <Route
            path="/incidents/:incidentId"
            element={<IncidentDetailPage />}
          />
        </Routes>
      </main>
      {toast && (
        <div className="toast visible" role="status">
          {toast}
        </div>
      )}
    </div>
  );
}
