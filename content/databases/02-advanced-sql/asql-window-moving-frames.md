---
id: asql-window-moving-frames
title: Moving averages and frame modes
level: intermediate
minutes: 3
summary: A ROWS moving frame counts rows, not elapsed days.
sourceLesson: asql-window-functions
---

The shop orders in date order total 120, 45, 60, 200, 45, 90, 60 and 30. Their dates are distinct. A window frame is the subset of a partition used for the current row’s calculation.

### Moving averages

Explicit `ROWS` frames give sliding windows. A three-order moving average:

```sql
-- Use this row and two predecessors.
SELECT id, total,
  AVG(total) OVER (
    ORDER BY ordered_on
    ROWS BETWEEN 2 PRECEDING
         AND CURRENT ROW) AS avg3
FROM orders;
```

The frame holds the current row and up to two before it, so the average divides by however many rows the frame actually has:

```formula
avg3_i = (t_{i−2} + t_{i−1} + t_i) / 3
for i ≥ 3
avg3_1 = 120 / 1 = 120
avg3_2 = (120 + 45) / 2 = 82.5
avg3_3 = (120 + 45 + 60) / 3 = 75
where
avg3_i: the three-order moving average on row i
i: the row's position in date order, starting at 1
t_i, t_{i−1}, t_{i−2}: the order totals on row i and on the one and two rows before it
avg3_1, avg3_2, avg3_3: the moving average on rows 1, 2 and 3
≥: greater than or equal to; the general line applies only from row 3 onward
3: the frame size: 2 PRECEDING plus the current row
In words: from the third row on, average the current order and the two before it; the first two rows have fewer rows in their frame, so they average only 1 and 2 values.
```

Partial windows at the start are a common source of misleading charts.

Frame modes: `ROWS` counts physical rows, `RANGE` uses value distance (`RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW` in Postgres), and `GROUPS` counts peer groups. Both databases support all three.

The third frame averages 120, 45 and 60, producing 75. The sixth averages 200, 45 and 90, producing about 111.67. Those are three orders, which may span very different durations. A seven-day average asks a different question and needs a date-based RANGE or calendar aggregation. PostgreSQL supports interval offsets on suitable ordered date/time values; SQLite RANGE offsets need a suitable single numeric ordering expression for numerical distance.

AVG ignores NULL totals. If one of three rows has a NULL total, the divisor is two; a frame with no non-NULL total returns NULL. If incomplete frames should not be charted, calculate a matching COUNT(total) window and keep only rows with the required count in an outer query.

## Key takeaways
- A ROWS moving frame counts rows, not elapsed days.
- AVG divides by the number of non-NULL values actually present in its frame.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
