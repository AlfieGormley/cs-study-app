---
id: asql-median-rows
title: Medians from the middle one or two rows
level: advanced
minutes: 3
summary: Number only the non-NULL observations before selecting middle rows.
sourceLesson: asql-interview-problems
---

The shop non-NULL totals sorted ascending are 30, 45, 45, 60, 60, 90, 120 and 200. A median splits sorted observations in half; with an even count this lesson averages the two middle observations.

## 7. Median

Postgres has an ordered-set aggregate:

```sql
-- Average the middle sorted positions.
SELECT percentile_cont(0.5)
  WITHIN GROUP (ORDER BY total)
FROM orders;
-- 60
```

`percentile_cont` interpolates between the two middle values; `percentile_disc` returns an actual value from the data. The SQLite/PostgreSQL version below assumes non-NULL totals and averages the middle one or two rows. Filter NULL totals before numbering to match percentile_cont, which ignores them; other SQL engines may require explicit integer division:

```sql
-- Average the middle sorted positions.
WITH s AS (
  SELECT total,
    ROW_NUMBER() OVER (
      ORDER BY total) AS rn,
    COUNT(*) OVER () AS n
  FROM orders
)
SELECT AVG(total) AS median
FROM s
WHERE rn IN ((n + 1) / 2,
             (n + 2) / 2);
```

The two `IN` positions come from integer division:

```formula
p_lo = ⌊(n + 1) / 2⌋
p_hi = ⌊(n + 2) / 2⌋
n = 8: ⌊9 / 2⌋ = 4, ⌊10 / 2⌋ = 5
n = 7: ⌊8 / 2⌋ = 4, ⌊9 / 2⌋ = 4
where
p_lo, p_hi: the row numbers (rn) of the lower and upper middle rows
n: the number of non-NULL totals, COUNT(*) OVER ()
⌊ ⌋: floor: round down to a whole number, which is what integer division does for positive numbers
In words: for an even count the two expressions pick the two middle rows, and for an odd count they both pick the single middle row; averaging them gives the median.
```

With eight rows the positions are fourth and fifth (both 60), so the median is 60. With seven rows both expressions select the fourth row, the single middle observation.

## Key takeaways
- Number only the non-NULL observations before selecting middle rows.
- Continuous percentiles can interpolate; discrete percentiles return observed values.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
