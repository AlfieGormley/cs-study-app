---
id: asql-rollup-grouping
title: ROLLUP, grouping sets and real NULLs
level: intermediate
minutes: 3
summary: ROLLUP makes successive prefix subtotals and a grand total.
sourceLesson: asql-set-ops-pivot
---

The shop has customers in Leeds, London and York. Its eight orders total 650. A grouping set is a list of columns that defines one aggregation level; an empty grouping set makes a grand total.

## Subtotals: ROLLUP and GROUPING SETS

A report with a grand-total row:

```sql
-- Add a grand total beside city groups.
-- Postgres
SELECT c.city, COUNT(*) AS n,
       SUM(o.total) AS revenue
FROM orders o
JOIN customers c
  ON c.id = o.customer_id
GROUP BY ROLLUP (c.city)
ORDER BY c.city;
```

| city | n | revenue |
|---|---|---|
| Leeds | 2 | 135 |
| London | 5 | 470 |
| York | 1 | 45 |
| NULL | 8 | 650 |

The NULL row is the total (Postgres sorts NULLs last in ascending order). The number of rows follows from the groupings ROLLUP asks for:

```formula
G_ROLLUP = k + 1
G_CUBE = 2^k
N = 3 + 1 = 4
where
G_ROLLUP: how many groupings ROLLUP computes: the full list, then each shorter prefix, down to the empty grouping (the grand total)
G_CUBE: how many groupings CUBE computes: every subset of the listed columns
k: the number of columns listed inside ROLLUP or CUBE, here 1 (city)
2^k: k copies of 2 multiplied together
N: the rows in this ROLLUP (c.city) result: 3 city rows plus 1 grand-total row
In words: ROLLUP of k columns makes k + 1 levels of subtotal, while CUBE makes every combination, 2^k of them; each grouping set contributes one row per distinct value combination.
```

Use the `GROUPING(c.city)` function to tell "total" NULLs apart from real NULL cities. `GROUPING SETS` and `CUBE` generalise this to any combination of groupings, within one query; the physical plan can use multiple sorts or aggregation phases.

SQLite has none of these. The equivalent is a `UNION ALL` of the grouped query and an ungrouped one, whose straightforward plan reads the inputs for both branches; a stored intermediate result can change that.

A real NULL city and the grand total can both display as NULL. Add GROUPING(c.city) to the SELECT list: zero means the grouping includes city, even when that city value is NULL; one means city was omitted for that subtotal. Do not infer the level by testing city IS NULL.

For ROLLUP(city, name), there is one row per city/name pair, one subtotal per city and one grand total. Five distinct customers across three cities therefore produce nine rows. This counts output groups, not just the three grouping sets. On an empty input the empty grouping set still produces a grand-total aggregate row, whereas nonempty grouping sets have no groups.

## Key takeaways
- ROLLUP makes successive prefix subtotals and a grand total.
- GROUPING distinguishes a subtotal placeholder from a real NULL key.

## Further reading
- [PostgreSQL 18: queries union](https://www.postgresql.org/docs/18/queries-union.html)
- [PostgreSQL 18: queries table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_select.html)
