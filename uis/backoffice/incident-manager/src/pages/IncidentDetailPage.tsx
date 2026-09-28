import { useState } from "react";
import { useParams } from "react-router-dom";
import { useCatalogs } from "../hooks/useCatalogs";
import { useIncidentDetail } from "../hooks/useIncidentDetail";
import {
  useIncidentAction,
  useUpdateIncident,
} from "../hooks/useIncidentMutations";
import { readable, formatDate, isOverdue, transitions } from "../lib/format";
import { Dialog } from "../components/Dialog";
import { Pill } from "../components/Pill";
import { DetailValue } from "../components/DetailValue";
import { IncidentFields } from "../components/IncidentFields";

export function IncidentDetailPage() {
  const { incidentId } = useParams();
  const [editing, setEditing] = useState(false);
  const { data: catalogs } = useCatalogs();
  const { data, isLoading, error } = useIncidentDetail(incidentId);
  const mutation = useIncidentAction(incidentId);
  const updateIncident = useUpdateIncident(incidentId);
  if (isLoading || !catalogs)
    return (
      <Dialog>
        <div className="loading-state">Loading incident...</div>
      </Dialog>
    );
  if (error)
    return (
      <Dialog>
        <div className="empty-state">{error.message}</div>
      </Dialog>
    );
  const incident = data.incident;
  if (editing)
    return (
      <Dialog>
        <p className="eyebrow">Incident {incident.id.slice(0, 8)}</p>
        <h2 id="modal-title">Edit incident</h2>
        <IncidentFields
          catalogs={catalogs}
          incident={incident}
          onSubmit={(payload) =>
            updateIncident.mutate(payload, {
              onSuccess: () => setEditing(false),
            })
          }
          submitLabel="Save changes"
        />
      </Dialog>
    );
  return (
    <Dialog>
      <div className="detail-header">
        <p className="eyebrow">Incident {incident.id.slice(0, 8)}</p>
        <h2 id="modal-title">{incident.title}</h2>
        <div className="detail-meta">
          <Pill value={incident.severity} />
          <Pill value={incident.status} />
          <Pill value={incident.channel} />
        </div>
        <div className="action-row">
          <button
            className="button button-quiet"
            type="button"
            onClick={() => setEditing(true)}
          >
            Edit details
          </button>
        </div>
      </div>
      <div className="detail-section">
        <p className="eyebrow">Lifecycle</p>
        <div className="action-row">
          {(transitions[incident.status] || []).map((status) => (
            <button
              className={`button ${status === "closed" ? "button-danger" : "button-primary"}`}
              type="button"
              key={status}
              onClick={() =>
                mutation.mutate({
                  path: `/incidents/${incidentId}/status`,
                  payload: { status },
                })
              }
            >
              Move to {readable(status)}
            </button>
          ))}
        </div>
      </div>
      <div className="detail-section">
        <p>{incident.description}</p>
        <div className="detail-grid">
          <DetailValue
            label="Responsible area"
            value={readable(incident.responsible_area)}
          />
          <DetailValue label="Reporter" value={incident.reporter} />
          <DetailValue
            label="Client/account"
            value={incident.client_account || "Not provided"}
          />
          <DetailValue
            label="SLA target"
            value={
              incident.sla_target_at
                ? `${formatDate(incident.sla_target_at)} · ${isOverdue(incident) ? "Overdue" : "On track"}`
                : "No SLA"
            }
          />
        </div>
        <div className="action-row">
          <select
            id="assignment-select"
            defaultValue={incident.responsible_area}
          >
            {catalogs.responsible_areas.map((area) => (
              <option value={area} key={area}>
                {readable(area)}
              </option>
            ))}
          </select>
          <button
            className="button button-quiet"
            type="button"
            onClick={() =>
              mutation.mutate({
                path: `/incidents/${incidentId}/assignment`,
                payload: {
                  responsible_area: (
                    document.querySelector(
                      "#assignment-select",
                    ) as HTMLSelectElement
                  ).value,
                },
              })
            }
          >
            Reassign
          </button>
        </div>
      </div>
      <div className="detail-section">
        <p className="eyebrow">Audit history</p>
        {data.audit_history.length ? (
          data.audit_history.map((event) => (
            <div className="audit-item" key={event.id}>
              <span className="audit-marker" />
              <div>
                <strong>{readable(event.event_type)}</strong>:{" "}
                {readable(event.previous_value)} → {readable(event.new_value)}
                <br />
                <span className="audit-time">
                  {formatDate(event.occurred_at)} · {event.actor_id}
                  {event.reason ? ` · ${event.reason}` : ""}
                </span>
              </div>
            </div>
          ))
        ) : (
          <p className="result-count">No changes recorded yet.</p>
        )}
      </div>
    </Dialog>
  );
}
