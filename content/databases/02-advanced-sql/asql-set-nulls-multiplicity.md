---
id: asql-set-nulls-multiplicity
title: Set equality, NULLs and copy counts
level: intermediate
minutes: 3
summary: Set operators treat two NULLs as not distinct, unlike equality predicates.
sourceLesson: asql-set-ops-pivot
---

A set operator combines complete rows from two SELECT results. UNION, INTERSECT and EXCEPT remove duplicate rows by default; PostgreSQL additionally supports the ALL variants discussed here.

### NULLs are "not distinct"

Set operations compare rows using **distinctness**, not `=`. Two NULLs count as the same:

```sql
-- Compare whole rows, including NULLs.
SELECT NULL INTERSECT SELECT NULL;
-- one row: NULL
```

Contrast `WHERE NULL = NULL`, which is UNKNOWN. This makes `EXCEPT` a handy way to diff two tables that contain NULLs, where a join on `=` would miss matching rows.

### INTERSECT ALL and EXCEPT ALL

With `ALL`, rows are treated as a multiset: `EXCEPT ALL` removes one copy per matching row.

```sql
-- Compare whole rows, including NULLs.
-- Postgres
SELECT x FROM (VALUES (1),(1),(2))
  AS t(x)
EXCEPT ALL
SELECT 1;
-- 1, 2  (one of the 1s survives)
```

The left side has two copies of 1 and the right side one, so one copy of 1 survives. In general, EXCEPT ALL cancels copies one for one, and INTERSECT ALL keeps as many copies as both sides share:

```formula reference
c_EXCEPT = max(m − n, 0)
c_INTERSECT = min(m, n)
where
c_EXCEPT: how many copies of a row EXCEPT ALL returns
c_INTERSECT: how many copies of a row INTERSECT ALL returns
m: how many copies of the row the left query has
n: how many copies of the same row the right query has
max(a, b): the larger of a and b, so the count never goes below zero
min(a, b): the smaller of a and b
a, b: the two values compared by max or min
In words: EXCEPT ALL cancels copies one for one, so a row survives as many times as the left side has spare copies; INTERSECT ALL keeps as many copies as both sides share.
```

Postgres supports `INTERSECT ALL` and `EXCEPT ALL`; SQLite supports only `UNION ALL`.

## Set operations versus joins

Several set operations have join equivalents:

| Set operation | Join form |
|---|---|
| `A INTERSECT B` | `EXISTS` semi-join |
| `A EXCEPT B` | `NOT EXISTS` anti-join |

Products never ordered, two ways:

```sql
-- Compare whole rows, including NULLs.
SELECT id FROM products
EXCEPT
SELECT product_id FROM order_items;
-- 6 (Vase)
```

```sql
-- Compare whole rows, including NULLs.
SELECT id FROM products p
WHERE NOT EXISTS (
  SELECT 1 FROM order_items i
  WHERE i.product_id = p.id);
```

They differ in two ways. `EXCEPT` deduplicates the output, and it treats NULLs as equal. Use `EXCEPT` when you're comparing whole rows; use `NOT EXISTS` when you want other columns from the row being tested in the result.

## Key takeaways
- Set operators treat two NULLs as not distinct, unlike equality predicates.
- EXCEPT ALL subtracts copies; INTERSECT ALL keeps the smaller copy count.

## Further reading
- [PostgreSQL 18: queries union](https://www.postgresql.org/docs/18/queries-union.html)
- [PostgreSQL 18: queries table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_select.html)
