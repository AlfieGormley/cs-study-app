---
id: asql-window-functions
title: Window functions
level: intermediate
minutes: 15
summary: Computing across related rows without collapsing them, with ROW_NUMBER, RANK, DENSE_RANK, LAG and LEAD, running totals, moving averages, and the frame rules that trip everyone up.
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

```sql
fn(args) OVER (
  PARTITION BY ...   -- split into groups
  ORDER BY ...       -- order within each
  ROWS BETWEEN ...   -- the frame
)
```

- **`PARTITION BY`** splits rows into independent groups, like `GROUP BY` without collapsing. Omit it and the whole result is one partition.
- **`ORDER BY`** orders rows within each partition. Ranking and `LAG`/`LEAD` need a meaningful order for predictable results (the syntax also permits omitting it); for aggregates it also changes the default frame (see below).
- **The frame** picks which rows of the partition, relative to the current row, an aggregate sees.

Window functions run *after* `WHERE`, `GROUP BY` and `HAVING`, and before the final `ORDER BY` and `LIMIT`. That ordering explains several rules below.

## Aggregates as window functions

Ordinary aggregates such as SUM and AVG become window functions when you add `OVER`; PostgreSQL ordered-set and hypothetical-set aggregates are exceptions. An empty `OVER ()` means "all rows":

```sql
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

Each row gets its share of the 650 total. Note the `100.0`: with `total` stored as SQLite integers or PostgreSQL integer (not bigint/numeric), `100 * total / SUM(...)` does integer division and 45 becomes 6, not 6.9.

Comparing a row with its group:

```sql
SELECT customer_id AS cust, id,
  total - AVG(total) OVER (
    PARTITION BY customer_id) AS diff
FROM orders;
```

Ana's orders (120, 60, 60) average 80, so they show +40, -20 and -20.

## Ranking: ROW_NUMBER, RANK, DENSE_RANK

The three differ only in how they treat **ties**. Our totals contain two ties (60 twice, 45 twice):

```sql
SELECT id, total,
  ROW_NUMBER() OVER w AS rn,
  RANK()       OVER w AS rnk,
  DENSE_RANK() OVER w AS dr
FROM orders
WINDOW w AS (ORDER BY total DESC);
```

| total | rn | rnk | dr |
|---|---|---|---|
| 200 | 1 | 1 | 1 |
| 120 | 2 | 2 | 2 |
| 90 | 3 | 3 | 3 |
| 60 | 4 | 4 | 4 |
| 60 | 5 | 4 | 4 |
| 45 | 6 | 6 | 5 |
| 45 | 7 | 6 | 5 |
| 30 | 8 | 8 | 6 |

- **`ROW_NUMBER`**: always 1, 2, 3... Ties get different numbers, in an **arbitrary** order unless you add a tie-breaker such as `ORDER BY total DESC, id`.
- **`RANK`**: ties share a rank and leave a **gap** (4, 4, then 6). Like a sports table.
- **`DENSE_RANK`**: ties share a rank with **no gap** (4, 4, then 5). Use it for "the Nth highest distinct value".

The `WINDOW w AS (...)` clause names a window so you don't repeat it. Both SQLite and Postgres support it.

`NTILE(n)` splits rows into n roughly equal buckets (quartiles with `NTILE(4)`), and `PERCENT_RANK` and `CUME_DIST` give relative positions.

## Top-N per group

The most common real use of `ROW_NUMBER`: each customer's latest order.

```sql
SELECT cust, id, ordered_on
FROM (
  SELECT customer_id AS cust, id,
    ordered_on,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY ordered_on DESC
    ) AS rn
  FROM orders
) AS t
WHERE rn = 1;
```

| cust | id | ordered_on |
|---|---|---|
| 1 | 107 | 2026-03-15 |
| 2 | 106 | 2026-03-02 |
| 3 | 108 | 2026-03-28 |
| 4 | 105 | 2026-02-20 |

Why the wrapping subquery? Because window functions are computed *after* `WHERE`. Writing `WHERE ROW_NUMBER() OVER (...) = 1` fails in both databases (Postgres says `window functions are not allowed in WHERE`). Some warehouses (Snowflake, BigQuery, DuckDB) add a `QUALIFY` clause for exactly this; SQLite and Postgres do not.

Choose the function to match the business rule: `ROW_NUMBER` returns exactly one row per group even on ties, while `RANK() ... = 1` returns all tied rows.

## LAG and LEAD

`LAG(x)` reads `x` from the previous row in the window order; `LEAD(x)` reads the next. Month-over-month revenue:

```sql
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

The first row has no predecessor, so `LAG` returns NULL. Supply a default with the third argument, `LAG(rev, 1, 0)`, and an offset with the second (`LAG(rev, 12)` for year-over-year on monthly data).

Note the pattern: aggregate in a CTE first, then apply the window. Windows run after `GROUP BY`, so you *can* write `LAG(SUM(total)) OVER (...)` in one query, but the two-step form is easier to read.

## Running totals and frames

Add `ORDER BY` to an aggregate's window and it becomes cumulative:

```sql
SELECT customer_id AS cust,
  ordered_on, total,
  SUM(total) OVER (
    PARTITION BY customer_id
    ORDER BY ordered_on) AS running
FROM orders;
```

| cust | ordered_on | total | running |
|---|---|---|---|
| 1 | 2026-01-05 | 120 | 120 |
| 1 | 2026-02-11 | 60 | 180 |
| 1 | 2026-03-15 | 60 | 240 |
| 2 | 2026-01-09 | 45 | 45 |
| 2 | 2026-03-02 | 90 | 135 |

The running total restarts for each partition.

### The default frame and the ties trap

When a window has `ORDER BY` but no explicit frame, the SQL standard default is:

```sql
RANGE BETWEEN UNBOUNDED PRECEDING
          AND CURRENT ROW
```

`RANGE` means "up to and including all **peers** of the current row", where peers are rows with an equal `ORDER BY` value. With unique sort keys you never notice. With ties you do:

```sql
SELECT id, total,
  SUM(total) OVER (ORDER BY total)
    AS range_sum,
  SUM(total) OVER (ORDER BY total
    ROWS UNBOUNDED PRECEDING)
    AS rows_sum
FROM orders;
```

| id | total | range_sum | rows_sum |
|---|---|---|---|
| 108 | 30 | 30 | 30 |
| 102 | 45 | 120 | 75 |
| 105 | 45 | 120 | 120 |
| 103 | 60 | 240 | 180 |
| 107 | 60 | 240 | 240 |
| 106 | 90 | 330 | 330 |

The table shows one possible ordering of ties; without a tie-breaker the ROWS totals assigned to ids 102/105 or 103/107 can swap. Under `RANGE`, both 45s include each other, so both show 120. Under `ROWS`, each row adds exactly one row. Neither is wrong, but a "running total" that jumps by 90 in one row is usually a bug. If the sort key can tie, write `ROWS` or add a tie-breaker column.

### Moving averages

Explicit `ROWS` frames give sliding windows. A three-order moving average:

```sql
SELECT id, total,
  AVG(total) OVER (
    ORDER BY ordered_on
    ROWS BETWEEN 2 PRECEDING
         AND CURRENT ROW) AS avg3
FROM orders;
```

The first row averages just itself (120), the second averages two rows (82.5), and from the third row on it averages three: (120 + 45 + 60) / 3 = 75. Partial windows at the start are a common source of misleading charts.

Frame modes: `ROWS` counts physical rows, `RANGE` uses value distance (`RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW` in Postgres), and `GROUPS` counts peer groups. Both databases support all three.

### The LAST_VALUE trap

```sql
LAST_VALUE(total) OVER (
  ORDER BY ordered_on)
```

You might expect the last order's total (30) on every row. Here dates are unique, so each row returns *its own* total. With tied dates, the default frame also includes peers and LAST_VALUE can come from another tied row. The last row of that frame is the current row. Fix it by extending the frame:

```sql
LAST_VALUE(total) OVER (
  ORDER BY ordered_on
  ROWS BETWEEN UNBOUNDED PRECEDING
       AND UNBOUNDED FOLLOWING)
```

`FIRST_VALUE` doesn't have this problem, since the default frame always starts at the partition's first row.

## SQLite and Postgres differences

Window function semantics are standard and match closely (SQLite added them in 3.25, 2018). The differences you hit are in surrounding types:

| Topic | SQLite | Postgres |
|---|---|---|
| `AVG` of ints | float, `82.5` | numeric, `82.5000...` |
| `ROUND(x, n)` | any number | numeric only |
| Window in `WHERE` | error | error |
| `QUALIFY` | no | no |

In Postgres, `ROUND(some_double, 1)` fails with `function round(double precision, integer) does not exist`; cast to `numeric` first.

## Performance notes

- Each distinct `PARTITION BY`/`ORDER BY` combination typically needs a sort. Several windows sharing one definition (use `WINDOW w`) can share the sort.
- An index matching `(partition cols, order cols)` can let Postgres skip the sort.
- Top-N per group via `ROW_NUMBER` may still read or sort many input rows, although PostgreSQL 15+ can stop computing window values when an eligible run condition fails. For a few rows per group over a large table, a `LATERAL` join with `LIMIT` on an index can be far cheaper (see the interview problems lesson).

## Key takeaways
- Window functions compute across related rows without collapsing them; `PARTITION BY` groups, `ORDER BY` orders, the frame selects.
- `ROW_NUMBER` is always unique, `RANK` leaves gaps after ties, `DENSE_RANK` doesn't.
- Window functions run after `WHERE`, so filter on them in an outer query or CTE.
- With `ORDER BY` and no frame, aggregates use `RANGE ... CURRENT ROW`, which lumps ties together; use `ROWS` for a true row-by-row running total.
- `LAST_VALUE` needs an explicit frame reaching `UNBOUNDED FOLLOWING`.
- Watch integer division and Postgres's numeric-only `ROUND`.

## Further reading
- [Window functions tutorial — PostgreSQL docs](https://www.postgresql.org/docs/current/tutorial-window.html)
- [Window functions reference — PostgreSQL docs](https://www.postgresql.org/docs/current/functions-window.html)
- [Window functions — SQLite docs](https://www.sqlite.org/windowfunctions.html)
- [Window function (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Window_function_(SQL))
