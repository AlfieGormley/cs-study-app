const DAY_MS = 86400000;

// Compare local calendar dates, so yesterday is one day ago even across DST.
export function daysSinceCompletion(completedAt, now = Date.now()) {
  if (!Number.isFinite(completedAt) || completedAt <= 0 || !Number.isFinite(now)) return null;
  const completed = new Date(completedAt), current = new Date(now);
  if (!Number.isFinite(completed.getTime()) || !Number.isFinite(current.getTime())) return null;
  const day = (date) => Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) / DAY_MS;
  return Math.max(0, day(current) - day(completed));
}

export function normalizeCompletionRange(range) {
  const days = (value, fallback) => Number.isSafeInteger(value) && value >= 0 ? value : fallback;
  const min = days(range?.min, 1);
  return { enabled: range?.enabled === true, min, max: Math.max(min, days(range?.max, 10)) };
}
