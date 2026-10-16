---
id: asql-window-ranking
title: Ranks, peers and NTILE groups
level: intermediate
minutes: 4
summary: ROW_NUMBER numbers rows; RANK and DENSE_RANK give peers equal ranks.
sourceLesson: asql-window-functions
---

The shop order totals are 200, 120, 90, 60, 60, 45, 45 and 30 in descending order. A window partition is the independent group of rows visible to a window function.

## Ranking: ROW_NUMBER, RANK, DENSE_RANK

The three differ only in how they treat **tied rows**: rows with the same sort value. Our totals contain two ties (60 twice, 45 twice):

```sql
-- Compare tied and distinct positions.
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

`NTILE(k)` splits the rows of each partition into k NTILE groups, numbered 1 to k, as equally as possible (quartiles with `NTILE(4)`). When the rows don't divide evenly, the leftover rows go one each to the first NTILE groups:

```formula
q = ⌊n / k⌋
r = n mod k
q = ⌊8 / 3⌋ = 2,  r = 8 mod 3 = 2
where
n: the number of rows in the partition, here 8
k: the number of NTILE groups asked for, the argument of NTILE(k), here 3
q: the size of the smaller NTILE groups
r: how many NTILE groups get one extra row (size q + 1); these are the first r NTILE groups
⌊ ⌋: floor: round down to a whole number
mod: the remainder after whole-number division (8 = 2 × 3 + 2, so 8 mod 3 = 2)
In words: share the rows out evenly, then give the leftover rows one each to the first NTILE groups.
```

So 8 rows in 3 NTILE groups have sizes 3, 3 and 2. NTILE works on row positions, so two tied values can land in different NTILE groups. `PERCENT_RANK` and `CUME_DIST` give relative SQL ranking positions as fractions between 0 and 1.

## Key takeaways
- ROW_NUMBER numbers rows; RANK and DENSE_RANK give peers equal ranks.
- NTILE balances row counts and can split tied values across NTILE groups.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
