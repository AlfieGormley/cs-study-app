---
id: asql-window-aggregates
title: Window aggregates without losing rows
level: intermediate
minutes: 5
summary: A window aggregate preserves every input row while computing over related rows.
sourceLesson: asql-window-functions
---

`GROUP BY` answers questions like "total per customer", but it **collapses** rows: you get one row per group and lose the detail. Often you want both: every order, *and* that customer's running total, *and* the order's rank. That's what **window functions** do.

A window function computes a value for each row from a set of related rows (its *window*), and leaves every row in place.

> [!analogy] Real-world analogy: a mark sheet with the class average
> A school can report results two ways. A summary sheet lists one line per class with its average mark. A mark sheet lists every pupil, with their class's average printed on the same line as their own mark.
>
> **How it maps:** The summary sheet is `GROUP BY`: one row per group, the individual pupils gone. The mark sheet is a window function: `AVG(mark) OVER (PARTITION BY class)` keeps every pupil's row and adds the group figure beside it. The class is the partition.
>
> **Where it stops:** A window can do more than repeat one group figure: with ORDER BY and a frame, each row can see a different set of rows (running totals, moving averages), which no printed class average does.

```
GROUP BY customer      window over customer
+------+-------+       +-----+-------+-----+
| cust | sum   |       | id  | total | sum |
| Ana  | 240   |       | 101 | 120   | 240 |
+------+-------+       | 103 | 60    | 240 |
  3 rows -> 1          | 107 | 60    | 240 |
                       +-----+-------+-----+
                         3 rows -> 3
```

Examples use the shop's 8 orders, whose totals are 120, 45, 60, 200, 45, 90, 60 and 30 (650 in all).

## Anatomy of OVER

This is a syntax template; dots mark omitted expressions:

```text
fn(args) OVER (
  PARTITION BY ...   -- split into groups
  ORDER BY ...       -- order within each
  ROWS BETWEEN ...   -- the frame
)
```

- **`PARTITION BY`** splits rows into independent groups, like `GROUP BY` without collapsing. Omit it and the whole result is one partition.
- **`ORDER BY`** orders rows within each partition. Ranking and `LAG`/`LEAD` need a meaningful order for predictable results (the syntax also permits omitting it); for aggregates it also changes the default frame (examined in Running totals and peer-sensitive frames).
- **The window frame** picks which rows of the partition, relative to the current row, an aggregate sees.

Window functions run *after* `WHERE`, `GROUP BY` and `HAVING`, and before the final `ORDER BY` and `LIMIT`. That ordering explains several rules below.

## Aggregates as window functions

Ordinary aggregates such as SUM and AVG become window functions when you add `OVER`; PostgreSQL ordered-set and hypothetical-set aggregates are exceptions. An empty `OVER ()` means "all rows":

```sql
-- Keep rows while sharing an aggregate.
SELECT id, total,
  ROUND(100.0 * total
    / SUM(total) OVER (), 1) AS pct
FROM orders;
```

| id | total | pct |
|---|---|---|
| 101 | 120 | 18.5 |
| 102 | 45 | 6.9 |
| 104 | 200 | 30.8 |
| ... | ... | ... |

Each row gets its share of the 650 total: order 101's 120 is 18.46…% of 650, which `ROUND(..., 1)` shows as 18.5.

Note the `100.0` in the SQL. With `total` stored as SQLite integers or PostgreSQL integer (not numeric), `100 * total / SUM(...)` does **integer division**, which throws away the fraction. Order 102's 45 then shows 6 rather than 6.9: 4500 / 650 is 6.92…, and integer division keeps only the whole-number part. Writing `100.0` makes one operand a decimal, so the division keeps its fraction.

Comparing a row with its group:

```sql
-- Keep rows while sharing an aggregate.
SELECT customer_id AS cust, id,
  total - AVG(total) OVER (
    PARTITION BY customer_id) AS diff
FROM orders;
```

Each row's `diff` is its own total minus the average of its customer's orders. Ana's orders average 80, so her 120 shows +40: a bigger-than-usual order for her.

So Ana's three orders (120, 60, 60) show +40, −20 and −20. For exact non-NULL arithmetic these differences sum to zero; floating-point calculations can have rounding error.

A window sees the rows that survive WHERE. Filtering to customer 1 before computing `SUM(total) OVER ()` makes that window total 240, not the shop’s 650. To display Ana’s orders with the grand total, compute the window in an inner query and filter the customer in an outer query. An explicit frame from UNBOUNDED PRECEDING to UNBOUNDED FOLLOWING also covers a whole partition even when the window has ordering.

## Key takeaways
- A window aggregate preserves every input row while computing over related rows.
- Use decimal division for percentage shares; integer operands truncate in these examples.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
