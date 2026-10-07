---
id: sql-group-by
title: GROUP BY, HAVING and aggregates
level: intermediate
minutes: 13
summary: Turning rows into totals. COUNT, SUM and AVG, grouping rules, WHERE versus HAVING, conditional aggregation, and the join fan-out that silently doubles your numbers.
---

Most business questions are about totals, not individual rows. How many orders are pending? What has each customer spent? Which category earns the most? **Aggregate functions** collapse many rows into one value, and `GROUP BY` decides which rows get collapsed together.

This lesson uses the same shop schema as the rest of the module. Order totals (quantity × price, summed over each order's items) come out as 101 = £62, 102 = £80, 103 = £41, 104 = £70, 105 = £25 and 106 = £8.

## Aggregates over the whole table

With no `GROUP BY`, an aggregate treats the whole filtered table as one group and returns exactly one row:

```sql
SELECT SUM(price), MIN(price),
       MAX(price), AVG(price)
FROM products;
```

| SUM | MIN | MAX | AVG |
|---|---|---|---|
| 193 | 8 | 90 | 38.6 |

### Three kinds of COUNT

`COUNT` is the one people trip over, because it has three forms that answer different questions:

```sql
SELECT COUNT(*),
       COUNT(customer_id),
       COUNT(DISTINCT customer_id)
FROM orders;
```

| form | result | counts |
|---|---|---|
| `COUNT(*)` | 6 | rows |
| `COUNT(customer_id)` | 5 | non-NULL values |
| `COUNT(DISTINCT ...)` | 4 | distinct non-NULL values |

Guest order 106 has a NULL `customer_id`, so `COUNT(customer_id)` skips it. Asha placed two orders, so the distinct count drops to 4. The numeric aggregates shown here, along with `COUNT(column)`, ignore NULLs; lesson 4 looks at what that means for averages.

### Integer arithmetic

`SUM` of integers is an integer, and dividing two integers truncates. `SUM(qty) / COUNT(*)` over `order_items` is 14 / 9, which gives **1**, while `AVG(qty)` gives 1.555... Use `AVG`, or multiply by `1.0` first.

PostgreSQL differs in a useful way here: `AVG` of an integer column returns `numeric`, so you see `38.6000000000000000` rather than SQLite's floating-point `38.6`. `SUM` of an `integer` column returns `bigint`, which widens the range but can still overflow at the 64-bit limit.

## GROUP BY: one row per group

`GROUP BY` splits the rows into groups that share the same values in the listed columns, then runs the aggregates once per group:

```sql
SELECT category,
       COUNT(*) AS n,
       AVG(price) AS avg_p
FROM products
GROUP BY category;
```

| category | n | avg_p |
|---|---|---|
| NULL | 1 | 8.0 |
| home | 2 | 65.0 |
| kitchen | 2 | 27.5 |

```
products        groups        result
Kettle  kit  ┐
Toaster kit  ┘─> kitchen ──> 2, 27.5
Lamp    home ┐
Rug     home ┘─> home    ──> 2, 65.0
Mug     NULL ──> NULL    ──> 1, 8.0
```

All NULL categories form **one** group, even though `NULL = NULL` is not true elsewhere in SQL.

You can group by an expression. Monthly order counts:

```sql
SELECT strftime('%Y-%m', ordered_on)
         AS month,
       COUNT(*) AS n
FROM orders
GROUP BY month;
```

That gives 2026-01: 1, 2026-02: 2 and 2026-03: 3. In PostgreSQL, with a real `date` column, you would write `date_trunc('month', ordered_on)` instead. Both databases allow `GROUP BY` to use a select-list alias; check support and name-resolution rules when moving to another SQL engine.

### The single-value rule

After grouping, each output row stands for a whole group. Every column in `SELECT` must therefore have one value per group: either it is in the `GROUP BY` list, or it is inside an aggregate.

```sql
SELECT customer_id, ordered_on,
       COUNT(*)
FROM orders
GROUP BY customer_id;
```

Asha has two orders with different dates. Which `ordered_on` should her row show?

- **PostgreSQL** refuses: `column "orders.ordered_on" must appear in the GROUP BY clause or be used in an aggregate function`.
- **SQLite** accepts it and picks the value from some row in the group. Here it showed 2026-01-05, but nothing guarantees which one. (MySQL behaves the same unless `ONLY_FULL_GROUP_BY` is on, which it is by default since 5.7.)

SQLite has one documented special case. If the query uses exactly one `MIN()` or `MAX()`, the bare columns come from the row that holds that minimum or maximum. `SELECT category, MAX(price), name ... GROUP BY category` returns Rug for home and Kettle for kitchen. It is convenient, but it is not portable. In PostgreSQL, the standard "row with the max per group" tool is `DISTINCT ON` or a window function (module 2).

PostgreSQL does relax the rule in one sensible case. If you group by a table's **primary key**, you may select any other column from that table, because the key determines them:

```sql
SELECT c.id, c.name, COUNT(o.id)
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
GROUP BY c.id;  -- name allowed
```

## WHERE versus HAVING

Both filter, but at different moments:

- `WHERE` filters **rows** before grouping. It cannot use aggregates.
- `HAVING` filters **groups** after aggregation. It can.

Who spent more than £50 on orders that were not cancelled?

```sql
SELECT o.customer_id,
       SUM(oi.qty * p.price) AS spent
FROM orders o
JOIN order_items oi
  ON oi.order_id = o.id
JOIN products p
  ON p.id = oi.product_id
WHERE o.status <> 'cancelled'
GROUP BY o.customer_id
HAVING SUM(oi.qty * p.price) > 50;
```

| customer_id | spent |
|---|---|
| 1 | 142 |
| 3 | 70 |

Asha (1) spent 62 + 80. Chloe (3) spent 70. Ben's 41 fails the `HAVING`. Dev's only order was cancelled, so `WHERE` removed it before grouping and he never forms a group.

Recall the logical order from lesson 1: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT. Two consequences:

1. Put row conditions in `WHERE` to state their intent clearly. Adding `status` to this query's `GROUP BY` changes its groups: a customer with both shipped and pending orders can produce two totals. It is not equivalent to filtering status before grouping by customer. The optimiser may also push eligible `HAVING` predicates down, so logical clause order does not dictate execution cost.
2. `HAVING` runs before `SELECT`, so in PostgreSQL you must repeat the aggregate: `HAVING spent > 50` fails with `column "spent" does not exist`. SQLite accepts the alias. `ORDER BY spent` works in both.

## Conditional aggregation

You often want several counts side by side. Put a condition inside the aggregate:

```sql
SELECT
  SUM(CASE WHEN status = 'shipped'
      THEN 1 ELSE 0 END) AS shipped,
  COUNT(*) FILTER
    (WHERE status = 'pending')
    AS pending
FROM orders;
```

| shipped | pending |
|---|---|
| 3 | 2 |

The `CASE` form works everywhere. The `FILTER` clause is standard SQL and reads better; PostgreSQL has supported it since 9.4 and SQLite since 3.30. This one-pass "pivot" is far cheaper than running a separate query per status.

## Joining strings

To list the names in each group, PostgreSQL has `string_agg(name, ', ' ORDER BY name)`. SQLite has long had `group_concat(name, ', ')` and added `string_agg` with in-aggregate `ORDER BY` in 3.44. Without the `ORDER BY` inside the call, the order of the joined names is unspecified.

## Empty input

What does `SUM(price)` return when no rows match?

```sql
SELECT SUM(price) FROM products
WHERE price > 1000;   -- NULL
SELECT COUNT(*) FROM products
WHERE price > 1000;   -- 0
```

`COUNT` of nothing is 0, but `SUM`, `AVG`, `MIN` and `MAX` of nothing are **NULL**. Wrap them in `COALESCE(SUM(price), 0)` when a report needs a zero. (SQLite also has a non-standard `TOTAL()` that returns 0.0.)

Add `GROUP BY` and the behaviour changes: no rows means no groups, so the query returns **zero rows**, not one row of NULL.

## Fan-out: the silent double count

The most expensive aggregate bug in real reporting comes from joins. A join repeats each row on the "one" side once per matching row on the "many" side. Aggregating after that repetition counts things more than once.

Counting orders per customer after joining `order_items`:

```sql
SELECT c.name, COUNT(*) AS n
FROM customers c
JOIN orders o
  ON o.customer_id = c.id
JOIN order_items oi
  ON oi.order_id = o.id
GROUP BY c.id;
```

| name | n |
|---|---|
| Asha | 3 |
| Ben | 2 |
| Chloe | 2 |
| Dev | 1 |

Asha has two orders, not three. The count is of order **lines**. `COUNT(DISTINCT o.id)` fixes this case, but there is a nastier version that `DISTINCT` cannot always rescue. Joining two independent one-to-many relationships at once multiplies them:

```sql
SELECT c.name,
       COUNT(o.id) AS orders,
       COUNT(r.id) AS refs
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
LEFT JOIN customers r
  ON r.referred_by = c.id
GROUP BY c.id;
```

| name | orders | refs |
|---|---|---|
| Asha | 4 | 4 |
| Ben | 1 | 1 |
| Erin | 0 | 0 |

(Chloe and Dev, with one order and no referrals, are left out to save space.) Asha has 2 orders and 2 referrals. The join produces 2 × 2 = 4 rows for her, so both counts say 4. `COUNT(DISTINCT ...)` would happen to fix counts here, but a `SUM` of order values would be doubled, and distinct sums are wrong whenever two real values are equal.

The reliable fix is to **aggregate each relationship separately, then join the results**, using subqueries or CTEs (module 2):

```sql
SELECT c.name,
  (SELECT COUNT(*) FROM orders o
   WHERE o.customer_id = c.id)
    AS orders,
  (SELECT COUNT(*) FROM customers r
   WHERE r.referred_by = c.id)
    AS refs
FROM customers c;
```

This gives Asha 2 and 2. A quick sanity check is to compare a grouped total with the same total computed without the join. If the numbers disagree, something is fanning out.

## LEFT JOIN plus COUNT

To include customers with zero orders, use a `LEFT JOIN` and count a column from the right-hand table:

| name | COUNT(*) | COUNT(o.id) |
|---|---|---|
| Asha | 2 | 2 |
| Erin | 1 | 0 |

(Ben, Chloe and Dev show 1 and 1.) Erin's row survives the outer join with NULLs in the order columns. `COUNT(*)` counts that row and reports 1. `COUNT(o.id)` skips the NULL and correctly reports 0.

## Key takeaways
- `COUNT(*)` counts rows; `COUNT(col)` counts non-NULL values; `COUNT(DISTINCT col)` counts distinct non-NULL values.
- Every selected column must be grouped or aggregated. PostgreSQL enforces this (allowing columns determined by a grouped primary key); SQLite silently picks a value.
- `WHERE` filters rows before grouping; `HAVING` filters groups after. PostgreSQL doesn't let `HAVING` use select aliases.
- `SUM` and friends return NULL on empty input; with `GROUP BY` you get no rows at all.
- Use `CASE` or `FILTER` inside aggregates for several counts in one pass.
- Joins fan out. Aggregate each one-to-many relationship separately, then combine.

## Further reading
- [Aggregate functions — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [GROUP BY and HAVING — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [Built-in aggregate functions — SQLite documentation](https://www.sqlite.org/lang_aggfunc.html)
- [Bare columns in aggregate queries — SQLite documentation](https://www.sqlite.org/lang_select.html#bare_columns_in_an_aggregate_query)
- [Aggregate expressions and FILTER — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-AGGREGATES)
