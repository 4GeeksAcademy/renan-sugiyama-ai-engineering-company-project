import { useNavigate } from "react-router-dom";
import { useSummary } from "../hooks/useSummary";
import { useUiStore } from "../store/uiStore";
import { readable } from "../lib/format";
import type { Catalogs } from "../types";

export function SummaryCards({ catalogs }: { catalogs: Catalogs }) {
  const navigate = useNavigate();
  const setFilter = useUiStore((state) => state.setFilter);
  const { data } = useSummary();
  if (!data)
    return <section className="summary-grid" aria-label="Loading summary" />;
  return (
    <section className="summary-grid" aria-label="Incident operations summary">
      <article className="summary-card metric-card">
        <span className="severity-label">Open backlog</span>
        <h3>{data.open_backlog_count}</h3>
        <p>incidents not closed</p>
      </article>
      <article className="summary-card metric-card overdue-metric">
        <span className="severity-label">Critical SLA overdue</span>
        <h3>{data.overdue_open_incident_count}</h3>
        <p>past {data.sla_hours}h Critical target</p>
      </article>
      <article className="summary-card metric-card">
        <span className="severity-label">SLA compliance</span>
        <h3>
          {data.resolved_within_sla_percent === null
            ? "--"
            : `${data.resolved_within_sla_percent}%`}
        </h3>
        <p>resolved within target</p>
      </article>
      <article className="summary-card metric-card">
        <span className="severity-label">Avg resolution</span>
        <h3>
          {data.average_resolution_hours === null
            ? "--"
            : `${data.average_resolution_hours}h`}
        </h3>
        <p>historical resolved average</p>
      </article>
      {catalogs.severities.map((severity) => (
        <button
          className={`summary-card ${severity}`}
          key={severity}
          type="button"
          onClick={() => {
            setFilter("severity", severity);
            navigate("/");
          }}
        >
          <span className="severity-label">{readable(severity)}</span>
          <h3>{data.open_incident_counts_by_severity[severity] || 0}</h3>
          <p>open incidents</p>
        </button>
      ))}
    </section>
  );
}
