---
id: asql-window-offsets
title: LAG and LEAD across reporting rows
level: intermediate
minutes: 3
summary: LAG and LEAD read previous and next rows in window order.
sourceLesson: asql-window-functions
---

The shop orders have monthly revenue January 165, February 305 and March 180. ordered_on is an ISO date. First aggregate orders into one row per observed month; then compare neighbouring monthly rows.

## LAG and LEAD

`LAG(x)` reads `x` from the previous row in the window order; `LEAD(x)` reads the next. Month-over-month revenue:

```sql
-- Compare neighbouring monthly rows.
WITH m AS (
  SELECT strftime('%Y-%m', ordered_on)
           AS month,
         SUM(total) AS rev
  FROM orders GROUP BY month
)
SELECT month, rev,
  LAG(rev) OVER (ORDER BY month)
    AS prev,
  rev - LAG(rev) OVER (ORDER BY month)
    AS diff
FROM m;
```

| month | rev | prev | diff |
|---|---|---|---|
| 2026-01 | 165 | NULL | NULL |
| 2026-02 | 305 | 165 | 140 |
| 2026-03 | 180 | 305 | -125 |

The query is SQLite: `strftime` is SQLite's date formatter. PostgreSQL writes the month key as `to_char(ordered_on, 'YYYY-MM')` and gives the same rows.

The `diff` column is the month-over-month change: this month's revenue minus the previous row's. February is 140 up on January; March is 125 down on February, so its change is negative.

The first row has no predecessor, so `LAG` returns NULL, and NULL minus anything is NULL. Supply a default with the third argument, `LAG(rev, 1, 0)`, and an offset with the second (`LAG(rev, 12)` for year-over-year when every calendar month is present).

Note the pattern: aggregate in a CTE first, then apply the window. Windows run after `GROUP BY`, so you *can* write `LAG(SUM(total)) OVER (...)` in one query, but the two-step form is easier to read.

> [!analogy] Real-world analogy: the previous page of a diary
> Someone keeps a diary but only writes on days when something happened. "The previous page" is the last day they wrote, which is not necessarily yesterday.
>
> **How it maps:** LAG reads the previous row in the window order, like turning back one page. If a month has no row, LAG skips straight to the last month that does, just as the previous page can be weeks earlier.
>
> **Where it stops:** A diary's first page has nothing before it, and LAG returns NULL there unless you supply a default. And SQL needs the window ORDER BY to define "previous"; the table has no page order of its own.

The offset counts rows, not calendar time. If February is missing, March’s preceding row is January. A year-over-year chart therefore needs a complete month series before applying a twelve-row offset. Generate calendar months and left join sales first, as in the series unit, and decide whether a missing month means zero sales or unavailable information.

A supplied default applies only when the requested row is outside the partition. If a predecessor exists but its revenue is NULL, LAG returns that NULL; its third argument does not replace stored NULLs. LEAD has the same boundary rule in the forward direction. Neither function’s offset is constrained by the window frame used by an aggregate.

## Key takeaways
- LAG and LEAD read previous and next rows in window order.
- A missing predecessor produces NULL unless an explicit default is supplied.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
