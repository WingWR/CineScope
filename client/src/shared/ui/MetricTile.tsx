type MetricTileProps = {
  label: string;
  value: string;
  tone?: "amber" | "teal" | "red";
};

export function MetricTile({ label, value, tone = "amber" }: MetricTileProps) {
  return (
    <div className="metric-tile" data-tone={tone}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
