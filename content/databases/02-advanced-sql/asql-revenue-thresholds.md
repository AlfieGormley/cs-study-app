---
id: asql-revenue-thresholds
title: Finding the first cumulative threshold crossing
level: advanced
minutes: 3
summary: Calculate running revenue before filtering for the threshold.
sourceLesson: asql-interview-problems
---

orders has eight distinct dates in 2026 with totals 120, 45, 60, 200, 45, 90, 60 and 30. The dates are 5 and 9 January; 11, 14 and 20 February; 2, 15 and 28 March.

## 6. Running totals and thresholds

"On what date did cumulative revenue first reach 400?"

```sql
-- Compute the sum before filtering it.
WITH r AS (
  SELECT ordered_on,
    SUM(total) OVER (
      ORDER BY ordered_on) AS running
  FROM orders
)
SELECT MIN(ordered_on) FROM r
WHERE running >= 400;
-- 2026-02-14 (running = 425)
```

The query finds the first row whose running total reaches the threshold. In date order the running total is 120, 165, 225 and then 425: the fourth order, on 14 February, is the first to reach 400. Filtering with `running >= 400` keeps that row and every later one, and `MIN(ordered_on)` picks the earliest.

The window must be computed before filtering, hence the CTE. If two orders could share a date, decide whether the running total should step per order (`ROWS`, with a tie-breaker) or per day (the default `RANGE`).

## Key takeaways
- Calculate running revenue before filtering for the threshold.
- Choose per-day peers or per-order stepping explicitly.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
