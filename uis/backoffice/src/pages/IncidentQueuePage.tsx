import { useCatalogs } from "../hooks/useCatalogs";
import { SummaryCards } from "../components/SummaryCards";
import { QueueHeader } from "../components/QueueHeader";
import { IncidentTable } from "../components/IncidentTable";

export function IncidentQueuePage() {
  const {
    data: catalogs,
    isLoading: catalogsLoading,
    error: catalogsError,
  } = useCatalogs();
  if (catalogsLoading)
    return <div className="loading-state">Loading workspace...</div>;
  if (catalogsError)
    return (
      <div className="empty-state">
        Unable to connect to the incident API. Start FastAPI on port 8000.
      </div>
    );
  return (
    <>
      <SummaryCards catalogs={catalogs} />
      <section className="workspace-panel">
        <QueueHeader catalogs={catalogs} />
        <IncidentTable />
      </section>
    </>
  );
}
