---
id: asql-set-union
title: Set operators and duplicate preservation
level: intermediate
minutes: 5
summary: Set operators match columns by position and take names from the first branch.
sourceLesson: asql-set-ops-pivot
---

Joins combine tables **side by side**: more columns. Set operations combine query results **end to end**: more (or fewer) rows. Pivoting goes sideways again, turning row values into columns for reports.

This lesson uses the shop's orders by month:

| month | products bought |
|---|---|
| Jan | Rug, Kettle, Toaster, Mug |
| Feb | Kettle, Rug, Mug, Toaster |
| Mar | Rug, Lamp, Mug, Kettle |

## The three operators

The three operators are the set operations from maths: union, intersection and difference. Call January's products A and March's B:

```formula
A = {Kettle, Mug, Rug, Toaster}
B = {Kettle, Mug, Rug, Lamp}
A ∪ B = {Kettle, Lamp, Mug, Rug, Toaster}
A ∩ B = {Kettle, Mug, Rug}
A − B = {Toaster}
B − A = {Lamp}
where
A: the set of product names sold in January
B: the set of product names sold in March
{ }: a set: a collection of distinct items, in no particular order
Kettle, Mug, Rug, Toaster, Lamp: product names, the members of the sets
∪: union, SQL's UNION: everything in either set
∩: intersection, SQL's INTERSECT: only what is in both sets
−: set difference, SQL's EXCEPT: what is in the left set but not the right
In words: UNION combines both months, INTERSECT keeps products sold in both, and EXCEPT keeps products sold in the first month but not the second.
```

Set difference depends on operand order, just as numeric subtraction does. The card above shows Toaster in one direction and Lamp in the other.

In SQL:

```sql
-- Keep names missing from the other set.
SELECT p.name
FROM order_items i
JOIN orders o ON o.id = i.order_id
JOIN products p
  ON p.id = i.product_id
WHERE o.ordered_on LIKE '2026-01%'
EXCEPT
SELECT p.name
FROM order_items i
JOIN orders o ON o.id = i.order_id
JOIN products p
  ON p.id = i.product_id
WHERE o.ordered_on LIKE '2026-03%';
-- Toaster
```

"Sold in January but not March" is Toaster. `EXCEPT` is not symmetric: swap the sides and you get Lamp. Oracle traditionally spells this MINUS; newer releases also accept EXCEPT.

### The rules

1. **Same number of columns**, matched **by position**, not by name. The first query's column names become the result's names.
2. **Compatible types.** Postgres resolves a common type and errors if it can't (`SELECT 1 UNION SELECT 'y'` fails with `invalid input syntax for type integer`). SQLite, with its dynamic typing, happily mixes integers and text in one column.
3. **Duplicates are removed** by `UNION`, `INTERSECT` and `EXCEPT`. ALL variants preserve copies according to each operator’s rule; SQLite supports only UNION ALL.
4. **`ORDER BY` and `LIMIT` apply to the whole result** and go at the end. To order one branch, wrap it in a subquery.

### UNION vs UNION ALL

Illustrative output from branches of distinct names:

```text
-- Jan names UNION ALL Mar names
Kettle, Kettle, Lamp, Mug, Mug,
Rug, Rug, Toaster       -- 8 rows
-- with UNION: 5 rows
```

The row counts follow from the sizes of the sets:

```formula
N_ALL = |A| + |B| = 4 + 4 = 8
N_UNION = |A ∪ B|
N_UNION = |A| + |B| − |A ∩ B|
N_UNION = 4 + 4 − 3 = 5
where
N_ALL: the number of rows UNION ALL returns
N_UNION: the number of rows UNION returns
A, B: January's and March's product names (no repeats inside each)
|A|, |B|: the number of items in A and in B, 4 each
|A ∪ B|: the number of distinct names in either month
|A ∩ B|: the number of names in both months, here 3 (Kettle, Mug, Rug)
∪: union: everything in either set
∩: intersection: what is in both sets
In words: UNION ALL simply adds the two row counts; UNION counts each shared name once, so it subtracts the names the months have in common.
```

These counts treat each month as a list with no repeats. If a branch repeats a row, UNION ALL keeps every copy, while UNION also removes repeats within a branch.

`UNION` must remove duplicates, often using sorting or hashing; already ordered input can instead feed a Unique plan node. `UNION ALL` just appends. Use `UNION ALL` when duplicates are wanted, or when the projected rows are unique both within each branch and across branches. Disjoint date filters alone do not prove projected names or totals are distinct; a source tag distinguishes branches but does not remove duplicates within one. This is one of the cheapest performance wins in SQL.

## Key takeaways
- Set operators match columns by position and take names from the first branch.
- Use UNION ALL when every copy is required or projected rows are already unique.

## Further reading
- [PostgreSQL 18: queries union](https://www.postgresql.org/docs/18/queries-union.html)
- [PostgreSQL 18: queries table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_select.html)
