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

The three operators are the set operations from maths: union, intersection and difference. Comparing January's products (Kettle, Mug, Rug, Toaster) with March's (Kettle, Mug, Rug, Lamp):

| operator | keeps | Jan with Mar |
|---|---|---|
| `UNION` | rows in either result | Kettle, Lamp, Mug, Rug, Toaster |
| `INTERSECT` | rows in both | Kettle, Mug, Rug |
| `EXCEPT` | rows in the left, not the right | Toaster |

Set difference depends on operand order, just as numeric subtraction does. January EXCEPT March is Toaster; March EXCEPT January is Lamp.

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

This is SQLite, where `ordered_on` is ISO date text, so `LIKE '2026-01%'` picks January. PostgreSQL has no LIKE for a `date` (`operator does not exist: date ~~ unknown`); compare a date range instead, such as `o.ordered_on >= '2026-01-01' AND o.ordered_on < '2026-02-01'`.

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

UNION ALL simply adds the two row counts: 4 + 4 = 8. UNION counts each shared name once, so the three names sold in both months (Kettle, Mug, Rug) appear once each, leaving 5. These counts treat each month as a list with no repeats. If a branch repeats a row, UNION ALL keeps every copy, while UNION also removes repeats within a branch.

> [!analogy] Real-world analogy: combining two invitation lists
> Two organisers each bring a guest list. Stapling the lists together keeps everyone, including people invited by both. Copying them onto one clean list writes each guest once. Ticking only people on both lists, or only people on the first list but not the second, gives two more lists.
>
> **How it maps:** Stapling is `UNION ALL`; the clean list is `UNION`; "on both" is `INTERSECT`; "first but not second" is `EXCEPT`. Making the clean list takes extra effort, just as duplicate removal adds a sort or hash.
>
> **Where it stops:** People match guests by name. SQL matches whole rows column by column, by position: (Ana, London) and (Ana, Leeds) are different rows, and the branches' column names are never compared.

`UNION` must remove duplicates, often using sorting or hashing; already ordered input can instead feed a Unique plan node. `UNION ALL` just appends. Use `UNION ALL` when duplicates are wanted, or when the projected rows are unique both within each branch and across branches. Disjoint date filters alone do not prove projected names or totals are distinct; a source tag distinguishes branches but does not remove duplicates within one. This is one of the cheapest performance wins in SQL.

## Key takeaways
- Set operators match columns by position and take names from the first branch.
- Use UNION ALL when every copy is required or projected rows are already unique.

## Further reading
- [PostgreSQL 18: queries union](https://www.postgresql.org/docs/18/queries-union.html)
- [PostgreSQL 18: queries table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_select.html)
