import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Field } from "./Field";
import { SelectField } from "./SelectField";
import type { Catalogs, Incident, IncidentPayload } from "../types";

export function IncidentFields({
  catalogs,
  incident,
  onSubmit,
  submitLabel,
}: {
  catalogs: Catalogs;
  incident?: Incident;
  onSubmit: (payload: IncidentPayload) => void;
  submitLabel: string;
}) {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: incident?.title || "",
    description: incident?.description || "",
    channel: incident?.channel || "phone",
    type: incident?.type || catalogs.types[0],
    severity: incident?.severity || "medium",
    responsible_area:
      incident?.responsible_area || "customer_support_outsourced",
    reporter: incident?.reporter || "",
    client_account: incident?.client_account || "",
  });
  const update = (event) =>
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  const submit = (event) => {
    event.preventDefault();
    const payload = { ...form };
    if (!payload.client_account) delete payload.client_account;
    onSubmit(payload);
  };
  return (
    <form onSubmit={submit}>
      <div className="form-grid">
        <Field
          label="Title"
          name="title"
          value={form.title}
          onChange={update}
          required
          full
        />
        <Field
          label="Description"
          name="description"
          value={form.description}
          onChange={update}
          required
          textarea
          full
        />
        <SelectField
          label="Intake channel"
          name="channel"
          value={form.channel}
          options={catalogs.channels}
          onChange={update}
        />
        <SelectField
          label="Type"
          name="type"
          value={form.type}
          options={catalogs.types}
          onChange={update}
        />
        <SelectField
          label="Severity"
          name="severity"
          value={form.severity}
          options={catalogs.severities}
          onChange={update}
        />
        <SelectField
          label="Responsible area"
          name="responsible_area"
          value={form.responsible_area}
          options={catalogs.responsible_areas}
          onChange={update}
        />
        <Field
          label="Reporter"
          name="reporter"
          value={form.reporter}
          onChange={update}
          required
        />
        <Field
          label="Client or account"
          name="client_account"
          value={form.client_account}
          onChange={update}
        />
      </div>
      <div className="form-actions">
        <button
          className="button button-quiet"
          type="button"
          onClick={() => navigate(-1)}
        >
          Cancel
        </button>
        <button className="button button-primary" type="submit">
          {submitLabel}
        </button>
      </div>
    </form>
  );
}
