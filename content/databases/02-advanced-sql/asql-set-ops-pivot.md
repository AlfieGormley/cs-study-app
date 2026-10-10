---
id: asql-set-ops-pivot
title: Set operations and pivoting
level: intermediate
minutes: 13
summary: Combining result sets with UNION, INTERSECT and EXCEPT (and the precedence rule SQLite gets differently), then turning rows into columns and back with conditional aggregation, FILTER, ROLLUP and LATERAL.
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

Unlike subtraction of numbers, difference depends on the order: A − B is not B − A.

In SQL:

```sql
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

"Sold in January but not March" is Toaster. `EXCEPT` is not symmetric: swap the sides and you get Lamp. Oracle spells it `MINUS`.

### The rules

1. **Same number of columns**, matched **by position**, not by name. The first query's column names become the result's names.
2. **Compatible types.** Postgres resolves a common type and errors if it can't (`SELECT 1 UNION SELECT 'y'` fails with `invalid input syntax for type integer`). SQLite, with its dynamic typing, happily mixes integers and text in one column.
3. **Duplicates are removed** by `UNION`, `INTERSECT` and `EXCEPT`. Add `ALL` to keep them.
4. **`ORDER BY` and `LIMIT` apply to the whole result** and go at the end. To order one branch, wrap it in a subquery.

### UNION vs UNION ALL

```sql
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

`UNION` must deduplicate, which means sorting or hashing the whole combined result. `UNION ALL` just appends. Use `UNION ALL` when duplicates are wanted, or when the projected rows are unique both within each branch and across branches. Disjoint date filters alone do not prove projected names or totals are distinct; a source tag distinguishes branches but does not remove duplicates within one. This is one of the cheapest performance wins in SQL.

### NULLs are "not distinct"

Set operations compare rows using **distinctness**, not `=`. Two NULLs count as the same:

```sql
SELECT NULL INTERSECT SELECT NULL;
-- one row: NULL
```

Contrast `WHERE NULL = NULL`, which is UNKNOWN. This makes `EXCEPT` a handy way to diff two tables that contain NULLs, where a join on `=` would miss matching rows.

### INTERSECT ALL and EXCEPT ALL

With `ALL`, rows are treated as a multiset: `EXCEPT ALL` removes one copy per matching row.

```sql
-- Postgres
SELECT x FROM (VALUES (1),(1),(2))
  AS t(x)
EXCEPT ALL
SELECT 1;
-- 1, 2  (one of the 1s survives)
```

The PostgreSQL documentation states the rule as counts of copies:

```formula
c_EXCEPT = max(m − n, 0)
c_INTERSECT = min(m, n)
c_EXCEPT = max(2 − 1, 0) = 1   for x = 1
where
c_EXCEPT: how many copies of a row EXCEPT ALL returns
c_INTERSECT: how many copies of a row INTERSECT ALL returns
m: how many copies of the row the left query has, here 2 copies of 1
n: how many copies the right query has, here 1
max(a, b): the larger of a and b; max(…, 0) stops the count going below zero
min(a, b): the smaller of a and b
a, b: the two values being compared
x: the column of the example rows
In words: EXCEPT ALL cancels copies one for one, so a row survives as many times as the left side has spare copies; INTERSECT ALL keeps as many copies as both sides share.
```

Postgres supports `INTERSECT ALL` and `EXCEPT ALL`; SQLite supports only `UNION ALL`.

## The precedence trap

What does this return?

```sql
SELECT 1
UNION SELECT 2
INTERSECT SELECT 3;
```

| Database | Parses as | Result |
|---|---|---|
| Postgres | `1 UNION (2 ∩ 3)` | `1` |
| SQLite | `(1 ∪ 2) ∩ 3` | empty |

Using the set symbols from earlier:

```formula
R_PG = {1} ∪ ({2} ∩ {3}) = {1} ∪ ∅
R_PG = {1}
R_SQLite = ({1} ∪ {2}) ∩ {3}
R_SQLite = {1, 2} ∩ {3} = ∅
where
R_PG: the result as Postgres groups the query
R_SQLite: the result as SQLite groups it
{ }: a set of rows; {1} is the single row 1
∪: union (UNION): everything in either set
∩: intersection (INTERSECT): only what is in both sets
∅: the empty set: no rows
In words: Postgres intersects 2 with 3 first, finds nothing in common, and is left with 1; SQLite unions 1 and 2 first, and nothing in that result equals 3.
```

The SQL standard (followed by Postgres and SQL Server) gives `INTERSECT` **higher precedence** than `UNION` and `EXCEPT`, the way `*` binds tighter than `+`. SQLite evaluates compound selects strictly left to right. The two documented precedence rules give different answers.

> [!tip] Don't rely on precedence
> When mixing operators, make the order explicit. Postgres allows parentheses around whole queries; SQLite doesn't, so use subqueries: `SELECT * FROM (... UNION ...) INTERSECT ...`.

## Set operations versus joins

Several set operations have join equivalents:

| Set operation | Join form |
|---|---|
| `A INTERSECT B` | `EXISTS` semi-join |
| `A EXCEPT B` | `NOT EXISTS` anti-join |

Products never ordered, two ways:

```sql
SELECT id FROM products
EXCEPT
SELECT product_id FROM order_items;
-- 6 (Vase)
```

```sql
SELECT id FROM products p
WHERE NOT EXISTS (
  SELECT 1 FROM order_items i
  WHERE i.product_id = p.id);
```

They differ in two ways. `EXCEPT` deduplicates the output, and it treats NULLs as equal. Use `EXCEPT` when you're comparing whole rows; use `NOT EXISTS` when you want other columns of the outer table in the result.

## Pivoting: rows to columns

Reports often want categories across the top. Revenue by month and category:

```sql
SELECT
  strftime('%Y-%m', o.ordered_on)
    AS month,
  SUM(CASE WHEN p.category = 'Kitchen'
      THEN i.qty * p.price
      ELSE 0 END) AS kitchen,
  SUM(CASE WHEN p.category = 'Home'
      THEN i.qty * p.price
      ELSE 0 END) AS home
FROM orders o
JOIN order_items i
  ON i.order_id = o.id
JOIN products p
  ON p.id = i.product_id
GROUP BY month;
```

| month | kitchen | home |
|---|---|---|
| 2026-01 | 75 | 90 |
| 2026-02 | 125 | 180 |
| 2026-03 | 50 | 130 |

This is **conditional aggregation**: each output column is an aggregate over only the rows matching its condition. It works on every SQL database, which is why it is the portable way to pivot.

Each cell of the pivot is a sum over just the order lines that match its month and its column's category:

```formula
R(m, g) = Σ q_l × p_l for all l in L(m, g)
R(Jan, Kitchen) = 1 × 30 + 1 × 25 + 2 × 10
R(Jan, Kitchen) = 75
where
R(m, g): the revenue shown in month m's row, under category g's column
m: a month, the GROUP BY value
g: a category, the value tested in the column's CASE
L(m, g): the order lines in month m whose product is in category g
l: one order line
q_l: the quantity on line l (qty)
p_l: the unit price of line l's product (price)
Σ: sigma, "add up" the term after it for every line l listed
Jan, Kitchen: January and the Kitchen category
In words: a pivot cell adds up quantity times price for only the lines in that month and that category; every other line contributes 0 through ELSE 0.
```

Check that cell against the data: January's Kitchen revenue is order 101's Kettle (30) plus order 102's Toaster (25) and two Mugs (20), giving 75.

### FILTER: the cleaner spelling

Both Postgres (9.4+) and SQLite (3.30+) support the standard `FILTER` clause:

```sql
SUM(i.qty * p.price)
  FILTER (WHERE p.category = 'Home')
  AS home
```

One difference: if no rows match, `FILTER` gives NULL (the `SUM` of nothing), while `CASE ... ELSE 0` gives 0. `COUNT(*) FILTER (...)` gives 0 either way.

### ELSE 0 versus no ELSE

Counting orders per customer per month with a `LEFT JOIN` from customers:

| name | jan | feb | mar |
|---|---|---|---|
| Ana | 1 | 1 | 1 |
| Dev | 0 | 1 | 0 |
| Eve | 0 | NULL | NULL |

The `jan` column used `SUM(CASE ... THEN 1 ELSE 0 END)`, so Eve's NULL-padded row counts as 0. The others used `SUM(o.ordered_on LIKE '2026-02%')`, which relies on SQLite treating booleans as 0/1. For Eve, the `LIKE` on NULL is NULL, so the sum is NULL. Postgres rejects that shortcut outright (`function sum(boolean) does not exist`); write `COUNT(*) FILTER (WHERE ...)` or cast with `::int`.

### Dynamic pivots

In PostgreSQL and SQLite, a static pivot has fixed output columns. Generating "one column per category, whatever categories exist" therefore needs an additional step. Other engines may offer dynamic-pivot syntax. Options:

- Generate the SQL in application code after querying the distinct values.
- Postgres's `tablefunc` extension provides `crosstab()`, but you still declare the output columns.
- SQL Server and Oracle have a `PIVOT` operator, also with a fixed column list.
- Often best: return long (unpivoted) rows and pivot in the reporting tool or with pandas `pivot_table`.

## Unpivoting: columns to rows

The reverse turns a wide row into several narrow ones. The portable way is `UNION ALL`:

```sql
SELECT id, 'total' AS metric,
       total AS val
FROM orders
UNION ALL
SELECT id, 'cust', customer_id
FROM orders;
```

This scans the table once per branch. Postgres can do it in one pass with `LATERAL` and `VALUES`:

```sql
SELECT o.id, k.metric, k.val
FROM orders o
CROSS JOIN LATERAL (VALUES
  ('total', o.total),
  ('cust', o.customer_id)
) AS k(metric, val);
```

`LATERAL` lets a subquery in `FROM` refer to columns of tables to its left. SQLite doesn't support it.

## Subtotals: ROLLUP and GROUPING SETS

A report with a grand-total row:

```sql
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
2^k: 2 multiplied by itself k times
N: the rows in this ROLLUP (c.city) result: 3 city rows plus 1 grand-total row
In words: ROLLUP of k columns makes k + 1 levels of subtotal, while CUBE makes every combination, 2^k of them; each grouping set contributes one row per distinct value combination.
```

Use the `GROUPING(c.city)` function to tell "total" NULLs apart from real NULL cities. `GROUPING SETS` and `CUBE` generalise this to any combination of groupings, within one query; the physical plan can use multiple sorts or aggregation phases.

SQLite has none of these. The equivalent is a `UNION ALL` of the grouped query and an ungrouped one, which scans the data twice.

## Key takeaways
- `UNION`, `INTERSECT` and `EXCEPT` combine whole result sets by column position and remove duplicates; `ALL` keeps them.
- Prefer `UNION ALL` when duplicates should be preserved or the combined projected rows are already unique.
- Set operations treat NULLs as equal, unlike `=`.
- Postgres binds `INTERSECT` tighter than `UNION`/`EXCEPT`; SQLite goes left to right. Make mixed expressions explicit.
- Pivot portably with conditional aggregation (`CASE` or `FILTER`); columns must be known when the query is written.
- Postgres adds `EXCEPT ALL`, `INTERSECT ALL`, `LATERAL`, `ROLLUP`, `CUBE` and `GROUPING SETS`; SQLite needs `UNION ALL` workarounds.

## Further reading
- [Combining queries (UNION, INTERSECT, EXCEPT) — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-union.html)
- [Table expressions: LATERAL and GROUPING SETS — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [Set operations (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Set_operations_(SQL))
- [Pivot: rows to columns — Modern SQL](https://modern-sql.com/use-case/pivot)
- [FILTER clause — Modern SQL](https://modern-sql.com/feature/filter)
- [tablefunc (crosstab) — PostgreSQL docs](https://www.postgresql.org/docs/current/tablefunc.html)
