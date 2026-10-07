---
id: sql-joins
title: Joins
level: basic
minutes: 14
summary: Inner, left, right, full, self and cross joins with real result tables, plus the two classic bugs, filtering in WHERE instead of ON and row fan-out.
---

A relational database splits data across tables so each fact is stored once. A customer's name lives in `customers`; their orders live in `orders` and point back with `customer_id`. A **join** puts the pieces back together for one query.

Every join does the same thing underneath. Conceptually it pairs each row of one table with each row of another, then keeps the pairs that satisfy the **join condition**. The join *type* decides what happens to rows that find no partner.

## The shop schema

This module uses one small shop throughout. Here are the parts that matter for joins.

```
customers(id, name, city, referred_by)
products(id, name, price, category)
orders(id, customer_id, ordered_on,
       status)
order_items(order_id, product_id, qty)
```

| customers | city | referred_by |
|---|---|---|
| 1 Asha | London | NULL |
| 2 Ben | Leeds | 1 |
| 3 Chloe | NULL | 1 |
| 4 Dev | London | 2 |
| 5 Erin | Bristol | NULL |

| orders | customer_id | status |
|---|---|---|
| 101 | 1 | shipped |
| 102 | 1 | shipped |
| 103 | 2 | pending |
| 104 | 3 | shipped |
| 105 | 4 | cancelled |
| 106 | NULL | pending |

Two details are deliberate. **Erin has no orders**, and **order 106 is a guest order** with no customer. Those two rows are what make the join types behave differently.

Products are Kettle (1, £30), Toaster (2, £25), Lamp (3, £40), Rug (4, £90) and Mug (5, £8). `order_items` has nine rows; the Rug has never been ordered.

## INNER JOIN: only matching pairs

```sql
SELECT c.name, o.id
FROM customers c
JOIN orders o ON o.customer_id = c.id;
```

| name | id |
|---|---|
| Asha | 101 |
| Asha | 102 |
| Ben | 103 |
| Chloe | 104 |
| Dev | 105 |

`JOIN` means `INNER JOIN`. Only pairs where the condition is true survive. Erin vanishes (no order points at her) and order 106 vanishes (its `customer_id` is NULL, and `NULL = anything` is never true).

Notice that Asha appears **twice**. A join produces one row per matching *pair*, not one per customer. Keep that in mind; it causes the biggest bug in this lesson.

The letters `c` and `o` are **table aliases**. Always qualify columns (`o.id`, not `id`) once more than one table is involved; both tables here have an `id` column, so a bare `id` would be ambiguous and rejected.

> [!note] Row order
> Results above are shown in a tidy order, but SQL guarantees no order without `ORDER BY`. SQLite and PostgreSQL may return the same rows in different orders.

## LEFT JOIN: keep everything on the left

```sql
SELECT c.name, o.id
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id;
```

| name | id |
|---|---|
| Asha | 101 |
| Asha | 102 |
| Ben | 103 |
| Chloe | 104 |
| Dev | 105 |
| Erin | NULL |

A **LEFT (OUTER) JOIN** keeps every row of the left table. If a left row has no partner, it appears once with NULLs in all the right table's columns. Erin is back, with `id` NULL.

This is the join for questions like "all customers, with their orders if any". It is by far the most common outer join.

## RIGHT and FULL OUTER JOIN

A **RIGHT JOIN** is the mirror image: keep every row of the right table.

```sql
SELECT c.name, o.id
FROM customers c
RIGHT JOIN orders o
  ON o.customer_id = c.id;
```

This returns the five matched rows plus `NULL | 106`: the guest order is kept, Erin is not. Any right join can be rewritten as a left join by swapping the tables, and most teams do exactly that so queries read consistently left to right.

A **FULL OUTER JOIN** keeps unmatched rows from both sides.

```sql
SELECT c.name, o.id
FROM customers c
FULL JOIN orders o
  ON o.customer_id = c.id;
```

| name | id |
|---|---|
| Asha | 101 |
| Asha | 102 |
| Ben | 103 |
| Chloe | 104 |
| Dev | 105 |
| Erin | NULL |
| NULL | 106 |

Full joins are rarer. They suit reconciliation jobs: "compare yesterday's export with today's and show rows missing from either side".

> [!warning] Engine support
> PostgreSQL supports RIGHT and FULL joins. SQLite only added them in version 3.39 (2022), so older SQLite builds reject them. MySQL still has no FULL OUTER JOIN; a duplicate-preserving emulation uses a LEFT JOIN plus `UNION ALL` of only the unmatched right-side rows. A plain `UNION` removes duplicate output rows.

## The anti-join: rows with no match

"Which customers have never ordered?" is a LEFT JOIN followed by a test for the NULLs it creates.

```sql
SELECT c.name
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
WHERE o.id IS NULL;
```

The result is just `Erin`. The same pattern finds products nobody has bought (`Rug`).

Test a column that can never be NULL in a real match, such as the right table's primary key. If you tested a nullable column like `o.status`, a genuine match with a NULL status would be misreported as "no match". `NOT EXISTS` expresses the same idea and is often clearer; subqueries come in the next module. Avoid `NOT IN` against a nullable column; lesson 4 shows why it can silently return nothing.

## ON versus WHERE in an outer join

This is the classic outer join bug. Say you want every customer, plus their *shipped* orders. Where does the `status` filter go?

```sql
-- Filter in ON
SELECT c.name, o.id, o.status
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
 AND o.status = 'shipped';
```

| name | id | status |
|---|---|---|
| Asha | 101 | shipped |
| Asha | 102 | shipped |
| Ben | NULL | NULL |
| Chloe | 104 | shipped |
| Dev | NULL | NULL |
| Erin | NULL | NULL |

```sql
-- Filter in WHERE
SELECT c.name, o.id, o.status
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
WHERE o.status = 'shipped';
```

| name | id | status |
|---|---|---|
| Asha | 101 | shipped |
| Asha | 102 | shipped |
| Chloe | 104 | shipped |

Why the difference? The logical order is: build the join (using `ON`), *then* apply `WHERE`.

- In `ON`, the filter decides which right rows count as a **match**. Ben's only order is pending, so he has no match and is padded with NULLs, but he is kept.
- In `WHERE`, the filter runs **after** the padding. Ben has status `pending`, Dev has `cancelled`, and only Erin is NULL-padded. None satisfies `status = 'shipped'`, so all three are removed. The LEFT JOIN has quietly become an INNER JOIN.

The rule of thumb:

- Conditions on the **optional** (right) table go in `ON` if you want to keep unmatched left rows.
- Conditions that should remove **left** rows go in `WHERE`.

The reverse surprise exists too. Putting `AND c.city = 'London'` in the `ON` of a LEFT JOIN does *not* remove Ben, Chloe or Erin. It just stops them matching any order, so they come back padded with NULLs. To keep only London customers, that test belongs in `WHERE`. For an INNER JOIN, `ON` and `WHERE` filters give the same result.

## Joining through a link table

Orders and products have a many-to-many relationship, resolved by `order_items`. Getting product names for an order means two joins in a chain.

```sql
SELECT o.id, p.name, i.qty
FROM orders o
JOIN order_items i ON i.order_id = o.id
JOIN products p ON p.id = i.product_id
WHERE o.customer_id = 1;
```

| id | name | qty |
|---|---|---|
| 101 | Kettle | 1 |
| 101 | Mug | 4 |
| 102 | Lamp | 2 |

Each join adds one table and one condition. Joins are associative for inner joins, so the database is free to execute them in any order it thinks is cheapest; how it chooses is the subject of the query processing module.

> [!warning] Mixing LEFT and INNER
> `customers LEFT JOIN orders ... JOIN order_items ...` drops Erin again. Her padded row has `o.id` NULL, so the inner join to `order_items` finds no match. Once a table is optional, every join that hangs off it usually needs to be a LEFT JOIN too.

## Fan-out: when joins multiply rows

Because a join produces one row per matching pair, joining a parent to a child repeats the parent once per child. That is fine until you aggregate.

```sql
SELECT c.name,
       COUNT(o.id) AS n,
       COUNT(DISTINCT o.id) AS d
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items i ON i.order_id = o.id
GROUP BY c.name;
```

| name | n | d |
|---|---|---|
| Asha | 3 | 2 |
| Ben | 2 | 1 |
| Chloe | 2 | 1 |
| Dev | 1 | 1 |

Asha has two orders, but joining to items gives three rows (order 101 has two items). `COUNT(o.id)` says 3.

It gets worse when you join **two independent child tables** to the same parent. Asha has 2 orders and referred 2 customers. Joining both gives 2 × 2 = 4 rows, so both counts come out as 4.

```
Asha x orders(101,102)
     x referrals(Ben,Chloe)
= 4 rows: every order paired
  with every referral
```

Fixes, in order of preference:

1. Aggregate each child table separately (in a subquery or CTE), then join the one-row-per-parent results.
2. Use `COUNT(DISTINCT ...)` for counts. This does not work for `SUM`, because two different items can have the same value.

A useful habit: before trusting a total, ask "what is one row of this result?" If the answer is "one order item", a sum of order totals is wrong.

## Self joins

A table can be joined to itself. `customers.referred_by` points at another customer, so listing each customer with the name of whoever referred them needs two copies of the table with different aliases.

```sql
SELECT c.name, r.name AS referrer
FROM customers c
LEFT JOIN customers r
  ON r.id = c.referred_by;
```

| name | referrer |
|---|---|
| Asha | NULL |
| Ben | Asha |
| Chloe | Asha |
| Dev | Ben |
| Erin | NULL |

The aliases are what make it work: `c` is "the customer", `r` is "the referrer". With an inner join, Asha and Erin would disappear because nobody referred them.

Self joins also find pairs within a table. `ON a.city = b.city AND a.id < b.id` lists customers sharing a city (just Asha and Dev). The `a.id < b.id` stops each pair appearing twice and stops a row pairing with itself. Self joins handle one level of a hierarchy; walking a whole tree needs a recursive CTE.

## CROSS JOIN: every combination

```sql
SELECT COUNT(*)
FROM customers
CROSS JOIN products;
-- 25
```

A **cross join** (Cartesian product) pairs every row with every row: 5 customers × 5 products = 25. It is useful on purpose, for example to build a grid of every product for every store or date, which you then LEFT JOIN real sales onto so missing combinations show up as zero.

It is dangerous by accident. The old comma syntax `FROM customers c, orders o` is a cross join (30 rows here) until a `WHERE o.customer_id = c.id` turns it into an inner join. Forget the condition on two million-row tables and you have asked for a trillion rows.

> [!note] SQLite versus PostgreSQL
> SQLite (and MySQL) accept `JOIN` with no `ON` and treat it as a cross join. PostgreSQL rejects it as a syntax error: an inner or outer join must have `ON`, `USING` or `NATURAL`. Only `CROSS JOIN` may omit a condition. SQLite also treats `CROSS JOIN` as an instruction not to reorder the two tables, which PostgreSQL does not.

## USING and NATURAL

When the join columns have the same name in both tables, `USING` is shorthand.

```sql
-- products_v: a view of products
-- with id renamed to product_id
SELECT order_id, name, qty
FROM order_items
JOIN products_v USING (product_id);
```

`USING (product_id)` means `ON a.product_id = b.product_id`, and the output has a single merged `product_id` column instead of two.

`NATURAL JOIN` goes further and joins on **every** column name the two tables share. It is fragile. In our schema the only shared name between `customers` and `orders` is `id`, so `customers NATURAL JOIN orders` matches customer ids against order ids and returns **0 rows**, with no error. Adding a column like `created_at` to both tables later would silently change the meaning of every natural join. Prefer explicit `ON`.

## Choosing a join

| Question | Join |
|---|---|
| Rows with a match | INNER |
| All of A, B if any | LEFT |
| Unmatched on both sides | FULL |
| A with no B | LEFT + IS NULL |
| Every combination | CROSS |
| Row to row in one table | self |

## Key takeaways
- A join pairs rows and keeps pairs that satisfy the condition; the type decides what happens to unmatched rows.
- INNER keeps only matches. LEFT keeps every left row, padding missing right columns with NULL. FULL keeps unmatched rows from both sides.
- In an outer join, a filter on the optional table belongs in `ON`. A NULL-rejecting filter such as `WHERE o.status = 'shipped'` removes the padded rows and makes this equivalent to an inner join.
- Joins repeat parent rows once per child. Joining two child tables multiplies them, so aggregate each separately before joining.
- The anti-join (`LEFT JOIN ... WHERE right.pk IS NULL`) finds rows with no partner.
- Avoid `NATURAL JOIN`; PostgreSQL requires a join condition except on `CROSS JOIN`.

## Further reading
- [Joins between tables — PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial-join.html)
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [SELECT — SQLite docs](https://www.sqlite.org/lang_select.html)
- [SQLite 3.39.0 release notes (RIGHT and FULL JOIN)](https://sqlite.org/releaselog/3_39_0.html)
- [Join (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Join_(SQL))
