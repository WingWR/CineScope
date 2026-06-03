import { cx } from "./classes";

type MetricTileProps = {
  label: string;
  value: string;
  tone?: "amber" | "teal" | "red";
};

export function MetricTile({ label, value, tone = "amber" }: MetricTileProps) {
  const valueToneClass = {
    amber: "text-cinema-amber",
    teal: "text-cinema-teal",
    red: "text-cinema-red",
  }[tone];

  return (
    <div className="grid min-h-[76px] gap-[7px] rounded-xl border border-cinema-border bg-cinema-surface p-3.5" data-tone={tone}>
      <span className="text-[0.76rem] uppercase text-cinema-muted">{label}</span>
      <strong className={cx("text-[1.22rem]", valueToneClass)}>{value}</strong>
    </div>
  );
}
