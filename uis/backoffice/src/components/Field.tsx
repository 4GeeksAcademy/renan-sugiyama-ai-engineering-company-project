import type { FieldProps } from "../types";

export function Field({
  label,
  name,
  value,
  onChange,
  required,
  textarea,
  full,
}: FieldProps) {
  const Control = textarea ? "textarea" : "input";
  return (
    <div className={`form-field ${full ? "full" : ""}`}>
      <label>{label}</label>
      <Control
        name={name}
        value={value}
        onChange={onChange}
        required={required}
      />
    </div>
  );
}
