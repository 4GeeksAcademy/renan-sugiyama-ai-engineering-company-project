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
    <section className="summary-grid" aria-label="Open incidents by severity">
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
