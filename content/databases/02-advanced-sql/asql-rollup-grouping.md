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

The NULL row is the total (Postgres sorts NULLs last in ascending order). ROLLUP computes the full grouping, then each shorter prefix of its column list, down to the empty grouping that makes the grand total. With one column that is two groupings: one row per city (3) plus one grand-total row, 4 rows. CUBE instead computes every combination of the listed columns: for (city, name) that is both columns, city alone, name alone and neither.

> [!analogy] Real-world analogy: an itemised bill with subtotals
> A restaurant bill for a group lists each item under the person who ordered it, a subtotal under each person, and a grand total at the bottom.
>
> **How it maps:** The item lines are the most detailed grouping, each person's subtotal is a shorter prefix of the grouping list, and the grand total is the empty grouping. `ROLLUP (person, item)` produces all three levels in one result.
>
> **Where it stops:** A printed bill labels its subtotal lines. SQL marks them only by putting NULL in the rolled-up columns, which can look identical to a genuinely missing value; `GROUPING()` tells them apart.

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
