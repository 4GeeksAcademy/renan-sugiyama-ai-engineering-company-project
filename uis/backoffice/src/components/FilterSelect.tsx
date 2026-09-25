import { readable } from "../lib/format";
import type { FilterName } from "../types";

export function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: FilterName;
  value: string;
  options: string[];
  onChange: (name: FilterName, value: string) => void;
}) {
  return (
    <select
      aria-label={`Filter by ${readable(label)}`}
      value={value}
      onChange={(event) => onChange(label, event.target.value)}
    >
      <option value="">All {readable(label)}</option>
      {options.map((option) => (
        <option value={option} key={option}>
          {readable(option)}
        </option>
      ))}
    </select>
  );
}
