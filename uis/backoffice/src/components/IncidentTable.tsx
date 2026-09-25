import { Link, useNavigate } from "react-router-dom";
import { useUiStore } from "../store/uiStore";
import { useIncidents } from "../hooks/useIncidents";
import { readable, formatDate, isOverdue } from "../lib/format";
import { Pill } from "./Pill";

export function IncidentTable() {
  const { filters, page, setPage } = useUiStore();
  const navigate = useNavigate();
  const { data, isLoading, error } = useIncidents(filters, page);
  if (isLoading) return <div className="loading-state">Loading queue...</div>;
  if (error)
    return (
      <div className="empty-state">
        Unable to load incidents: {error.message}
      </div>
    );
  const totalPages = Math.max(data.total_pages, 1);
  return (
    <>
      <div className="result-count queue-count">
        {data.total_items} result{data.total_items === 1 ? "" : "s"}
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Incident</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Responsible area</th>
              <th>SLA</th>
              <th>Updated</th>
              <th>
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {data.items.length ? (
              data.items.map((incident) => (
                <tr key={incident.id}>
                  <td>
                    <Link
                      className="incident-link"
                      to={`/incidents/${incident.id}`}
                    >
                      {incident.title}
                    </Link>
                    <span className="incident-id">
                      {incident.id.slice(0, 8)} · {readable(incident.channel)}
                    </span>
                  </td>
                  <td>
                    <Pill value={incident.severity} />
                  </td>
                  <td>
                    <Pill value={incident.status} />
                  </td>
                  <td>{readable(incident.responsible_area)}</td>
                  <td>
                    <span
                      className={`sla ${isOverdue(incident) ? "overdue" : "on-track"}`}
                    >
                      {isOverdue(incident) ? "OVERDUE" : "ON TRACK"}
                      <br />
                      {formatDate(incident.sla_target_at)}
                    </span>
                  </td>
                  <td>{formatDate(incident.updated_at)}</td>
                  <td>
                    <button
                      className="icon-button"
                      type="button"
                      onClick={() => navigate(`/incidents/${incident.id}`)}
                      aria-label="View incident"
                    >
                      →
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="empty-state">
                  No incidents match these filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="pagination">
        <button
          className="icon-button"
          type="button"
          disabled={page <= 1}
          onClick={() => setPage(page - 1)}
          aria-label="Previous page"
        >
          ←
        </button>
        <span>
          Page {data.page} of {totalPages}
        </span>
        <button
          className="icon-button"
          type="button"
          disabled={page >= totalPages}
          onClick={() => setPage(page + 1)}
          aria-label="Next page"
        >
          →
        </button>
      </div>
    </>
  );
}
