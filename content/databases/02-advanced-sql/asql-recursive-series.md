---
id: asql-recursive-series
title: Filling missing reporting months
level: intermediate
minutes: 3
summary: Generate the required months before a LEFT JOIN so months without orders survive.
sourceLesson: asql-ctes
---

A sparse sales table cannot produce a row for a month it never recorded. The shop has orders in January, February and March 2026, totalling 165, 305 and 180; April has none. A recursive CTE can supply the calendar independently.

### Filling gaps in a series

Reports need a row for every month, even months with no sales. Generate the months, then `LEFT JOIN`:

```sql
-- Supply months that orders cannot.
WITH RECURSIVE months(m) AS (
  SELECT '2026-01-01'
  UNION ALL
  SELECT date(m, '+1 month')
  FROM months
  WHERE m < '2026-04-01'
)
SELECT strftime('%Y-%m', m) AS month,
       COALESCE(SUM(o.total), 0) AS rev
FROM months
LEFT JOIN orders o
  ON strftime('%Y-%m', o.ordered_on)
   = strftime('%Y-%m', m)
GROUP BY m
ORDER BY m;
```

| month | rev |
|---|---|
| 2026-01 | 165 |
| 2026-02 | 305 |
| 2026-03 | 180 |
| 2026-04 | 0 |

Postgres has a built-in for this, so you rarely need recursion there:

```sql
-- Supply months that orders cannot.
SELECT m::date
FROM generate_series(
  date '2026-01-01',
  date '2026-04-01',
  interval '1 month') AS m;
```

The LEFT JOIN is doing essential work: the generated April row has no matching order, so its order columns are NULL. SUM ignores NULL values and has no contributing value there, so it returns NULL. COALESCE supplies zero. Putting an order-date filter in WHERE after the join could discard that calendar row again; restrict matching orders in ON.

The termination test reads the previous month. April is generated from March, then April fails the test and creates no May row. This example deliberately starts on the first of a month. Calendar arithmetic at the end of a month needs a separate rule because month lengths differ. PostgreSQL generate_series returns a set of timestamps here; the cast presents the date.

## Key takeaways
- Generate the required months before a LEFT JOIN so months without orders survive.
- SUM over an empty match is NULL; COALESCE turns it into a reporting zero.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
