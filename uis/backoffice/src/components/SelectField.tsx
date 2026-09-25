import { readable } from "../lib/format";
import type { ChangeHandler } from "../types";

export function SelectField({
  label,
  name,
  value,
  options,
  onChange,
}: {
  label: string;
  name: string;
  value: string;
  options: string[];
  onChange: ChangeHandler;
}) {
  return (
    <div className="form-field">
      <label>{label}</label>
      <select name={name} value={value} onChange={onChange}>
        {options.map((option) => (
          <option value={option} key={option}>
            {readable(option)}
          </option>
        ))}
      </select>
    </div>
  );
}
