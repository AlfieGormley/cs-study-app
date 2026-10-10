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
- **The window frame** picks which rows of the partition, relative to the current row, an aggregate sees.

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

So Ana's three orders (120, 60, 60) show +40, −20 and −20. The differences in one partition always add up to 0.

## Ranking: ROW_NUMBER, RANK, DENSE_RANK

The three differ only in how they treat **tied rows**: rows with the same sort value. Our totals contain two ties (60 twice, 45 twice):

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

You can work out either rank by counting what sorts ahead of the row:

```formula
RANK = 1 + N_ahead
DENSE_RANK = 1 + D_ahead
RANK = 1 + 5 = 6
DENSE_RANK = 1 + 4 = 5
where
RANK: the value RANK() gives the row
DENSE_RANK: the value DENSE_RANK() gives the row
N_ahead: the number of rows that sort strictly before this one (tied rows don't count); for a 45 these are 200, 120, 90, 60 and 60, so 5
D_ahead: the number of distinct sort values strictly before this one; for a 45 these are 200, 120, 90 and 60, so 4
In words: for an order of 45, five rows but only four distinct values sort ahead. RANK counts every row ahead of you, so ties ahead push you down further; DENSE_RANK counts only different values ahead, so it never skips a number.
```

So DENSE_RANK can never be larger than RANK, and the two agree up to and including the first group of tied rows; they differ from the row after it.

The `WINDOW w AS (...)` clause names a window so you don't repeat it. Both SQLite and Postgres support it.

`NTILE(k)` splits the rows of each partition into k buckets, numbered 1 to k, as equally as possible (quartiles with `NTILE(4)`). When the rows don't divide evenly, the leftover rows go one each to the first buckets:

```formula
q = ⌊n / k⌋
r = n mod k
q = ⌊8 / 3⌋ = 2,  r = 8 mod 3 = 2
where
n: the number of rows in the partition, here 8
k: the number of buckets asked for, the argument of NTILE(k), here 3
q: the size of the smaller buckets
r: how many buckets get one extra row (size q + 1); these are the first r buckets
⌊ ⌋: floor: round down to a whole number
mod: the remainder after whole-number division (8 = 2 × 3 + 2, so 8 mod 3 = 2)
In words: share the rows out evenly, then give the leftover rows one each to the first buckets.
```

So 8 rows in 3 buckets have sizes 3, 3 and 2. NTILE works on row positions, so two tied values can land in different buckets. `PERCENT_RANK` and `CUME_DIST` give relative positions as fractions between 0 and 1.

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

The `diff` column is a month-over-month change:

```formula
diff_m = rev_m − rev_{m−1}
diff_Feb = 305 − 165 = 140
diff_Mar = 180 − 305 = −125
where
diff_m: the change in revenue from the previous month to month m
rev_m: the revenue of month m, the SUM of that month's order totals
rev_{m−1}: the revenue of the month before m; this is what LAG(rev) reads
m: a month, counted in window order
diff_Feb, diff_Mar: the February and March changes, worked out from the table above
In words: each month's change is its revenue minus the previous month's revenue; a negative answer means revenue fell.
```

The first row has no predecessor, so `LAG` returns NULL, and NULL minus anything is NULL. Supply a default with the third argument, `LAG(rev, 1, 0)`, and an offset with the second (`LAG(rev, 12)` for year-over-year on monthly data).

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

The running total restarts for each partition. Written as a sum:

```formula
S_i = Σ t_j   for j = 1 to i
S_2 = t_1 + t_2 = 120 + 60 = 180
S_3 = 120 + 60 + 60 = 240
where
S_i: the running total on row i of a partition
i: the row's position within its partition, in ORDER BY order, starting at 1
j: a counter that steps through the positions 1, 2, …, i
t_j: the order total on row j
S_2, S_3, t_1, t_2: the running total on rows 2 and 3, and the totals on rows 1 and 2
Σ: sigma, "add up": add the term after it for every value of j listed
In words: the running total on a row is the sum of every total from the first row of its partition up to and including that row.
```

These are customer 1's rows: 180 on the second row, 240 on the third.

### The default frame and the ties trap

When a window has `ORDER BY` but no explicit frame, the SQL standard default is:

```sql
RANGE BETWEEN UNBOUNDED PRECEDING
          AND CURRENT ROW
```

`RANGE` means "up to and including all **peer rows** of the current row", where peer rows (peers) are rows with an equal `ORDER BY` value. With unique sort keys you never notice. With ties you do:

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

The table shows one possible ordering of ties; without a tie-breaker the ROWS totals assigned to ids 102/105 or 103/107 can swap. Under `RANGE`, both 45s include each other, so both show 120. Under `ROWS`, each row adds exactly one row. The two frames sum different sets of rows:

```formula
S_RANGE(i) = Σ t_j for all j with v_j ≤ v_i
S_ROWS(i) = Σ t_j for all j ≤ i
S_RANGE = 30 + 45 + 45 = 120
S_ROWS = 30 + 45 = 75
where
S_RANGE(i): the default RANGE frame's sum on row i
S_ROWS(i): the ROWS UNBOUNDED PRECEDING sum on row i
i: the current row's position in sort order, starting at 1; the worked lines are for order 102, the first 45, at position 2
j: the position of another row in the same partition
t_j: the total on row j
v_i, v_j: the ORDER BY values of rows i and j, here the totals themselves
Σ: sigma, "add up" the term after it for every j that meets the condition
≤: less than or equal to; with ascending order, v_j ≤ v_i means "sorts at or before row i, peers included"
In words: RANGE adds every row whose sort value is no bigger than the current row's, ties included; ROWS adds only the rows physically up to the current one.
```

Neither is wrong, but a "running total" that jumps by 90 in one row is usually a bug. If the sort key can tie, write `ROWS` or add a tie-breaker column.

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

The frame holds the current row and up to two before it, so the average divides by however many rows the frame actually has:

```formula
avg3_i = (t_{i−2} + t_{i−1} + t_i) / 3
avg3_1 = 120 / 1 = 120
avg3_2 = (120 + 45) / 2 = 82.5
avg3_3 = (120 + 45 + 60) / 3 = 75
where
avg3_i: the three-order moving average on row i
i: the row's position in date order, starting at 1
t_i, t_{i−1}, t_{i−2}: the order totals on row i and on the one and two rows before it
avg3_1, avg3_2, avg3_3: the moving average on rows 1, 2 and 3
3: the frame size: 2 PRECEDING plus the current row
In words: from the third row on, average the current order and the two before it; the first two rows have fewer rows in their frame, so they average only 1 and 2 values.
```

Partial windows at the start are a common source of misleading charts.

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
