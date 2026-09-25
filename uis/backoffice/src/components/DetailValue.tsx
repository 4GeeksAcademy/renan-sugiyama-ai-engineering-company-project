export function DetailValue({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value}</span>
    </div>
  );
}
