export function formatRating(value: number): string {
  return value.toFixed(1);
}

export function formatOptionalRating(value?: number): string {
  return typeof value === "number" ? formatRating(value) : "-";
}

export function formatRuntime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const remaining = minutes % 60;
  return hours > 0 ? `${hours}h ${remaining}m` : `${remaining}m`;
}

export function formatOptionalRuntime(minutes?: number): string {
  return typeof minutes === "number" ? formatRuntime(minutes) : "Pending";
}

export function formatMoney(value: number): string {
  if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(1)}B`;
  }

  if (value >= 1_000_000) {
    return `$${Math.round(value / 1_000_000)}M`;
  }

  if (value >= 1_000) {
    return `$${Math.round(value / 1_000)}K`;
  }

  return `$${value.toLocaleString("en-US")}`;
}

export function formatOptionalMoney(value?: number): string {
  return typeof value === "number" ? formatMoney(value) : "Pending";
}

export function formatScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}
