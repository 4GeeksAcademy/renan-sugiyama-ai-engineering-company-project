import { useNavigate } from "react-router-dom";
import { useCatalogs } from "../hooks/useCatalogs";
import { useCreateIncident } from "../hooks/useIncidentMutations";
import { Dialog } from "../components/Dialog";
import { IncidentFields } from "../components/IncidentFields";

export function IncidentFormPage() {
  const navigate = useNavigate();
  const { data: catalogs } = useCatalogs();
  const mutation = useCreateIncident(() => navigate("/"));
  if (!catalogs)
    return (
      <Dialog>
        <div className="loading-state">Loading form...</div>
      </Dialog>
    );
  return (
    <Dialog>
      <p className="eyebrow">New record</p>
      <h2 id="modal-title">Register incident</h2>
      <IncidentFields
        catalogs={catalogs}
        onSubmit={(payload) => mutation.mutate(payload)}
        submitLabel="Create incident"
      />
    </Dialog>
  );
}
