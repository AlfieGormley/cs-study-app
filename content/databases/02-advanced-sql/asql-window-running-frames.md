---
id: asql-window-running-frames
title: Running totals and peer-sensitive frames
level: intermediate
minutes: 5
summary: The ordered default frame includes all peers of the current row.
sourceLesson: asql-window-functions
---

The shop orders sum to 650. Ana, customer 1, has 120 on 5 January, 60 on 11 February and 60 on 15 March 2026. Window frames choose which rows contribute to each aggregate.

## Running totals and frames

Add `ORDER BY` to an aggregate's window and it becomes cumulative:

```sql
-- The frame decides which rows add up.
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
-- The frame decides which rows add up.
RANGE BETWEEN UNBOUNDED PRECEDING
          AND CURRENT ROW
```

`RANGE` means "up to and including all **peer rows** of the current row", where peer rows (peers) are rows with an equal `ORDER BY` value. With unique ordering values you never notice. With ties you do:

```sql
-- The frame decides which rows add up.
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

A peer-group running total is useful for totals per price band or per day. A per-order total needs ROWS plus a deterministic ordering, such as `ORDER BY total, id`; ROWS alone does not decide which tied row goes first. The window ORDER BY controls the calculation, while a final query ORDER BY controls the displayed result order. A later LIMIT does not redefine which rows contributed.

## Key takeaways
- The ordered default frame includes all peers of the current row.
- ROWS needs a deterministic tie-breaker for a repeatable per-row running total.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
