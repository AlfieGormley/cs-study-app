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

> [!analogy] Real-world analogy: a race with a dead heat
> Two runners are judged a dead heat for third place. The results printout still has to put one of their names on the line above the other, the official placings give both third place and award no fourth, and a count of different finishing times would call the next runner the fourth time recorded.
>
> **How it maps:** The printout's line numbers are `ROW_NUMBER`: every row gets its own number, even among ties. The official placings are `RANK`: tied rows share a rank and the next rank is skipped. Counting different finishing times is `DENSE_RANK`: tied rows share a rank and no number is skipped.
>
> **Where it stops:** Whoever prints the results can choose a rule for which tied runner goes first, such as alphabetical order; `ROW_NUMBER` follows no rule of its own, so the order among tied rows is unspecified unless the window ORDER BY includes a tie-breaker. Placing conventions also vary between sports; the analogy uses the common one in which a shared place skips the next.

You can predict either rank by counting what sorts ahead of the row. **RANK is 1 plus the number of rows strictly ahead**, so ties ahead push it down. **DENSE_RANK is 1 plus the number of distinct values strictly ahead**, so it never skips a number. For an order of 45, five rows (200, 120, 90, 60, 60) but only four distinct values sort ahead: RANK 6, DENSE_RANK 5.

So DENSE_RANK can never be larger than RANK, and the two agree up to and including the first group of tied rows; they differ from the row after it.

The `WINDOW w AS (...)` clause names a window so you don't repeat it. Both SQLite and Postgres support it.

`NTILE(k)` splits the rows of each partition into k NTILE groups, numbered 1 to k, as equally as possible (quartiles with `NTILE(4)`). When the rows don't divide evenly, the groups differ in size by at most one, and the leftover rows go one each to the first NTILE groups. So 8 rows in 3 NTILE groups have sizes 3, 3 and 2. NTILE works on row positions, so two tied values can land in different NTILE groups. `PERCENT_RANK` and `CUME_DIST` give relative SQL ranking positions as fractions between 0 and 1.

## Key takeaways
- ROW_NUMBER numbers rows; RANK and DENSE_RANK give peers equal ranks.
- NTILE balances row counts and can split tied values across NTILE groups.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
