import { readable } from "../lib/format";

export function Pill({ value }: { value: string }) {
  return <span className={`pill ${value}`}>{readable(value)}</span>;
}
