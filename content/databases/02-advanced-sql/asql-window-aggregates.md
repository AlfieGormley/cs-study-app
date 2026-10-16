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

Each row gets its share of the 650 total. The query computes this percentage for every row:

```formula
pct = round(100 × t / T, 1)
pct = round(100 × 120 / 650, 1)
pct = round(18.46…, 1) = 18.5 %
where
pct: the row's share of all revenue, as a percentage (%)
t: this row's order total, here 120 (order 101); the lesson's totals are plain amounts with no currency given
T: the sum of every order total in the window, here 650; `SUM(total) OVER ()` computes it
round(x, 1): round x to 1 decimal place, as SQL's ROUND(x, 1) does
100: converts a fraction (0.1846) into a percentage (18.46)
…: the digits carry on (18.4615…)
%: per cent, parts per hundred
In words: divide the row's total by the grand total, multiply by 100 to get a percentage, then round to one decimal place.
```

Note the `100.0` in the SQL. With `total` stored as SQLite integers or PostgreSQL integer (not bigint/numeric), `100 * total / SUM(...)` does **integer division**, which throws away the fraction:

```formula
pct = trunc(100 × 45 / 650)
pct = trunc(6.92…) = 6
where
pct: the percentage SQL returns when every operand is an integer
45: order 102's total
650: the grand total of all orders
trunc(x): truncation: drop everything after the decimal point, rounding towards zero
…: the digits carry on (6.923…)
In words: when every value is a whole number, SQL keeps only the whole-number part of the division, so 6.92 becomes 6.
```

Writing `100.0` makes one operand a decimal, so the division keeps its fraction and 45 gives 6.9.

Comparing a row with its group:

```sql
-- Keep rows while sharing an aggregate.
SELECT customer_id AS cust, id,
  total - AVG(total) OVER (
    PARTITION BY customer_id) AS diff
FROM orders;
```

Each row's `diff` is its own total minus the average of its partition:

```formula
diff = t − avg_c
avg_c = (120 + 60 + 60) / 3 = 80
diff = 120 − 80 = +40
where
diff: how far this order is above (+) or below (−) its customer's average order
t: this order's total, here 120 (Ana's order 101)
avg_c: the mean (average) total of all orders by the same customer c: their sum divided by how many there are
c: the customer the row belongs to, here Ana; `PARTITION BY customer_id` decides which rows share c
In words: subtract the customer's average order from this order; a positive answer means a bigger-than-usual order for that customer.
```

So Ana's three orders (120, 60, 60) show +40, −20 and −20. For exact non-NULL arithmetic these differences sum to zero; floating-point calculations can have rounding error.

A window sees the rows that survive WHERE. Filtering to customer 1 before computing `SUM(total) OVER ()` makes that window total 240, not the shop’s 650. To display Ana’s orders with the grand total, compute the window in an inner query and filter the customer in an outer query. An explicit frame from UNBOUNDED PRECEDING to UNBOUNDED FOLLOWING also covers a whole partition even when the window has ordering.

## Key takeaways
- A window aggregate preserves every input row while computing over related rows.
- Use decimal division for percentage shares; integer operands truncate in these examples.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
