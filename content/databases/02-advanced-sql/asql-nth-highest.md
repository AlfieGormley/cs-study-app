---
id: asql-nth-highest
title: Nth highest: distinct values and empty results
level: advanced
minutes: 3
summary: Decide whether Nth means a distinct value or a row position.
sourceLesson: asql-interview-problems
---

The shop totals are 200, 120, 90, 60, 60, 45, 45 and 30. They are non-NULL. Before solving an interview problem, agree its tie rule and whether insufficient data should return NULL or no row.

## 1. The Nth highest value

"Find the second-highest order total." Three standard answers:

```sql
-- Count distinct values, not tied rows.
-- A: nested MAX
SELECT MAX(total) AS second
FROM orders
WHERE total < (SELECT MAX(total)
               FROM orders);

-- B: DISTINCT + OFFSET
SELECT DISTINCT total
FROM orders
ORDER BY total DESC
LIMIT 1 OFFSET 1;

-- C: DENSE_RANK
WITH r AS (
  SELECT total, DENSE_RANK() OVER (
    ORDER BY total DESC) AS dr
  FROM orders)
SELECT DISTINCT total
FROM r WHERE dr = 2;
```

All three give 120 for the non-NULL totals shown. To ignore missing totals on arbitrary data, filter `total IS NOT NULL` before OFFSET or ranking; PostgreSQL DESC sorts NULLs first by default. Now the probes:

- **Generalise to N.** The nested MAX form shown is specifically the second-highest pattern; arbitrary positions need further nesting or another method. OFFSET skips one fewer row than the requested position, and DENSE_RANK can filter on the desired rank. The fourth distinct total is 60.
- **Forgot DISTINCT?** With ties, the 5th highest via `ORDER BY total DESC LIMIT 1 OFFSET 4` without `DISTINCT` lands on the second 60 rather than 45. `ROW_NUMBER` makes the same mistake; `DENSE_RANK` is the ranking that means "Nth distinct value".
- **Fewer than N values.** A returns one row containing NULL. B and C return **no rows**. If the spec says "return NULL", wrap it as a scalar subquery: `SELECT (SELECT DISTINCT total ... OFFSET 8) AS nth` gives a single NULL.

OFFSET counts the rows to *skip*, which is why B skips one fewer row than the requested position: the fourth highest distinct total needs `OFFSET 3`, skipping 200, 120 and 90 to land on 60.

## Key takeaways
- Decide whether Nth means a distinct value or a row position.
- A scalar wrapper converts an empty result into one NULL.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
