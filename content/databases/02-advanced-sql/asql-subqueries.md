---
id: asql-subqueries
title: Subqueries and correlated subqueries
level: basic
minutes: 12
summary: Queries inside queries, from scalar and IN subqueries to correlated EXISTS, the NOT IN NULL trap, and how Postgres actually executes them.
---

A **subquery** is a complete `SELECT` placed inside another statement. It lets you ask a question whose answer depends on another question: "which orders are bigger than the *average* order?" You can't write the average as a constant because you don't know it yet, so you compute it in a subquery.

Every lesson in this module uses the same small shop. Result tables show the expected output for the stated data.

> [!note] Content gap: execution provenance
> Original execution records were not available to this audit, so claims that every query was run in SQLite or that a particular PostgreSQL plan was observed are omitted. PostgreSQL-only syntax is labelled; plan shapes below are illustrative.

## The shop schema

```sql
customers(id, name, city)
products(id, name, category, price)
orders(id, customer_id, ordered_on, total)
order_items(order_id, product_id, qty)
```

| id | name | city |
|---|---|---|
| 1 | Ana | London |
| 2 | Ben | Leeds |
| 3 | Cat | London |
| 4 | Dev | York |
| 5 | Eve | Leeds |

| id | cust | date | total |
|---|---|---|---|
| 101 | 1 | 01-05 | 120 |
| 102 | 2 | 01-09 | 45 |
| 103 | 1 | 02-11 | 60 |
| 104 | 3 | 02-14 | 200 |
| 105 | 4 | 02-20 | 45 |
| 106 | 2 | 03-02 | 90 |
| 107 | 1 | 03-15 | 60 |
| 108 | 3 | 03-28 | 30 |

All dates are in 2026. Products are Kettle (30), Toaster (25), Mug (10) in *Kitchen*, and Lamp (40), Rug (90), Vase (35) in *Home*. Eve has never ordered, and nobody has bought a Vase. Those two gaps will matter.

## Where a subquery can go

A subquery's *shape* decides where it is allowed:

| Shape | Returns | Used in |
|---|---|---|
| Scalar | 0–1 rows, 1 col | `SELECT`, `WHERE`, `HAVING` |
| Column | n rows, 1 col | `IN`, `ANY`, `ALL` |
| Table | n rows, m cols | `FROM` |
| Existence | anything | `EXISTS` |

### Scalar subqueries

```sql
SELECT id, total
FROM orders
WHERE total > (SELECT AVG(total)
               FROM orders);
```

| id | total |
|---|---|
| 101 | 120 |
| 104 | 200 |
| 106 | 90 |

The inner query runs once, yields 81.25 (650 / 8), and the outer query compares each row with it. This is an **uncorrelated** subquery: it doesn't mention the outer query at all, so the database can evaluate it once and reuse the value.

> [!warning] A "scalar" subquery that returns two rows
> If a scalar subquery returns more than one row, **PostgreSQL raises an error**: `more than one row returned by a subquery used as an expression`. **SQLite silently uses the first row** it happens to find. A query that "works" in SQLite can fail in production on Postgres, and the SQLite answer was arbitrary anyway.

### IN with a column subquery

Customers who have bought a Rug (product 4):

```sql
SELECT name FROM customers
WHERE id IN (
  SELECT o.customer_id
  FROM orders o
  JOIN order_items i
    ON i.order_id = o.id
  WHERE i.product_id = 4);
```

The result is Ana, Ben and Cat. Each has one Rug order line in this fixture, so a plain join happens to return the same three customers. IN is a **semi-join**: it keeps each outer customer row at most once even if there are several matching lines. For example, switching the product to Kettle (id 1) finds Ana in orders 101 and 103; IN still returns her once, while the corresponding join returns her twice.

### Derived tables in FROM

A subquery in `FROM` acts like a temporary table. Average spend per customer, by city:

```sql
SELECT city, AVG(spend) AS avg_spend
FROM (
  SELECT c.city, c.id,
         SUM(o.total) AS spend
  FROM customers c
  JOIN orders o
    ON o.customer_id = c.id
  GROUP BY c.id
) AS per_cust
GROUP BY city;
```

| city | avg_spend |
|---|---|
| Leeds | 135.0 |
| London | 235.0 |
| York | 45.0 |

You need two levels of aggregation (sum per customer, then average per city), and SQL does not let you nest aggregates like `AVG(SUM(...))` directly. A derived table is the classic fix. The next lesson shows that a CTE says the same thing more readably.

Postgres before version 16 required the alias (`AS per_cust`); SQLite and Postgres 16+ accept it without one. Always alias anyway.

## Correlated subqueries

A **correlated** subquery refers to a column of the outer query. Conceptually it is re-evaluated for every outer row, with that row's values plugged in.

Each customer's most recent order:

```sql
SELECT o.id, c.name, o.ordered_on
FROM orders o
JOIN customers c
  ON c.id = o.customer_id
WHERE o.ordered_on = (
  SELECT MAX(o2.ordered_on)
  FROM orders o2
  WHERE o2.customer_id = o.customer_id
);
```

| id | name | ordered_on |
|---|---|---|
| 107 | Ana | 2026-03-15 |
| 106 | Ben | 2026-03-02 |
| 108 | Cat | 2026-03-28 |
| 105 | Dev | 2026-02-20 |

Trace it for order 103 (Ana, 11 Feb): the inner query becomes "max date among customer 1's orders", which is 15 March. 11 Feb doesn't equal it, so 103 is dropped. For 107 the dates match, so it stays.

The aliases `o` and `o2` are essential. Without them, `customer_id = customer_id` inside the subquery would refer to the inner table on both sides and be true for every row.

### Correlated subqueries in SELECT

```sql
SELECT c.name,
  (SELECT COUNT(*)
   FROM orders o
   WHERE o.customer_id = c.id) AS n
FROM customers c;
```

This returns Ana 3, Ben 2, Cat 2, Dev 1 and **Eve 0**. `COUNT(*)` over zero rows is 0, so customers with no orders still appear. An equivalent `LEFT JOIN ... GROUP BY` works too; the subquery form is often clearer when you want one extra figure per row.

## EXISTS and NOT EXISTS

`EXISTS (subquery)` is true if the subquery returns at least one row. What it selects is irrelevant, so `SELECT 1` is the convention.

Customers who have never ordered:

```sql
SELECT c.name
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.id);
```

Result: Eve. The same pattern on `products` and `order_items` finds Vase. This is an **anti-join**: keep outer rows with *no* match.

## The NOT IN trap

`NOT IN` looks like it should be the same as `NOT EXISTS`. It isn't, because of NULL.

```sql
SELECT name FROM customers
WHERE id NOT IN (2, 3, NULL);
-- returns no rows at all
```

Work through it for Ana (id 1). `1 NOT IN (2, 3, NULL)` means `1 <> 2 AND 1 <> 3 AND 1 <> NULL`. The last term is UNKNOWN, and `TRUE AND UNKNOWN` is UNKNOWN. `WHERE` keeps only TRUE rows, so Ana is dropped. So is everyone else.

In real code the NULL arrives through a subquery: `WHERE id NOT IN (SELECT referrer_id FROM ...)` where one row has a NULL `referrer_id`. The query silently returns nothing.

> [!tip] Prefer NOT EXISTS
> `NOT EXISTS` compares row by row with `=` inside the subquery, and a NULL there simply fails to match. It never poisons the whole result. If you must use `NOT IN`, add `WHERE col IS NOT NULL` to the subquery.

`IN` with a NULL in the list still gives UNKNOWN for nonmatching values; in this positive WHERE filter that does not change which rows survive: `id IN (2, 3, NULL)` still returns Ben and Cat, because `OR` with one TRUE term is TRUE.

## ANY, ALL and row values

PostgreSQL supports quantified comparisons. Orders bigger than *every* one of Ana's:

```sql
SELECT id FROM orders
WHERE total > ALL (
  SELECT total FROM orders
  WHERE customer_id = 1);
-- 104 (200 beats 120, 60, 60)
```

`= ANY (...)` is the same as `IN`. **SQLite does not support `ANY`/`ALL`**; for a nonempty set of non-NULL values, `> (SELECT MAX(...))` gives the same result as `> ALL (...)`. NULLs also matter: MAX ignores them, while ALL can return UNKNOWN. Watch the empty-set edge case: `> ALL` of an empty set is TRUE, whereas comparing with `MAX` of an empty set gives NULL, which filters everything out.

Both databases accept row-value comparisons such as `WHERE (id, city) IN (SELECT ...)`.

## How databases actually run them

"Re-evaluated for every outer row" is the *meaning*, not necessarily the *plan*. Optimisers rewrite subqueries into joins whenever the semantics allow. These are possible PostgreSQL plan shapes, not a guarantee for this small dataset:

| Query form | Postgres plan |
|---|---|
| `IN (subquery)` | Hash (semi) join |
| `NOT EXISTS` | Hash anti join |
| `NOT IN (subquery)` | Hashed SubPlan |
| Correlated scalar | SubPlan per row |

The interesting row is `NOT IN`. Because of the NULL semantics above, Postgres cannot turn it into an anti-join. When the subquery result is small it builds a hash table of it (a "hashed SubPlan"). If the planner estimates that hash will exceed its hash-memory budget (`work_mem × hash_mem_multiplier`), it uses a plain SubPlan that rescans the subquery for each outer row, which can be catastrophically slow on large tables. That is a second reason to prefer `NOT EXISTS`.

A correlated scalar subquery in `SELECT` typically runs as a SubPlan once per outer row. With an index on `orders(customer_id)` that is fine for a few thousand rows; across millions of rows, a single `GROUP BY` and join is usually much cheaper.

> [!note] Which form should you write?
> Write whichever form states the question most clearly, then check the plan with `EXPLAIN`. `EXISTS` and `IN` can use semi-joins; an ordinary join can return duplicates and need a different plan. Investigate expensive `NOT IN` and per-row scalar subqueries, preserving their intended NULL and duplicate semantics when rewriting.

## Key takeaways
- A subquery's shape (scalar, column, table, existence) decides where it can appear.
- `IN` and `EXISTS` are semi-joins: they never duplicate outer rows, unlike a plain join.
- A correlated subquery references the outer row; alias both tables so the correlation is unambiguous.
- `NOT IN` returns nothing if the list contains a NULL. Use `NOT EXISTS` for anti-joins.
- Postgres errors on a scalar subquery returning several rows; SQLite quietly takes the first.
- Optimisers turn `IN`/`EXISTS` into joins, but not `NOT IN`; check plans with `EXPLAIN`.

## Further reading
- [Subquery expressions — PostgreSQL docs](https://www.postgresql.org/docs/current/functions-subquery.html)
- [Correlated subquery — Wikipedia](https://en.wikipedia.org/wiki/Correlated_subquery)
- [SELECT — SQLite docs](https://www.sqlite.org/lang_select.html)
- [Don't Do This: NOT IN — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
