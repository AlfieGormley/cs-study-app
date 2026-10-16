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

The query finds the first row whose running total reaches the threshold:

```formula
S_i = t_1 + t_2 + … + t_i
S_3 = 120 + 45 + 60 = 225
S_4 = 225 + 200 = 425 ≥ 400
where
S_i: the running total after the i-th order in date order
t_1, t_2, t_i: the totals of the 1st, 2nd and i-th orders
…: and every order in between
i: the position in date order, starting at 1
S_3, S_4: the running totals after the 3rd and 4th orders
≥: greater than or equal to
400: the threshold the question asks about
In words: keep adding totals in date order; the first row where the sum is at least 400 is the 4th order, on 14 February.
```

The window must be computed before filtering, hence the CTE. If two orders could share a date, decide whether the running total should step per order (`ROWS`, with a tie-breaker) or per day (the default `RANGE`).

## Key takeaways
- Calculate running revenue before filtering for the threshold.
- Choose per-day peers or per-order stepping explicitly.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
