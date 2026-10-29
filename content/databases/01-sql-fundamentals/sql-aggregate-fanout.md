---
id: sql-aggregate-fanout
title: Protect aggregates from join fan-out
level: intermediate
minutes: 5
sourceLesson: sql-group-by
summary: A count after joining lines counts lines rather than orders.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## Fan-out: the silent double count

The most expensive aggregate bug in real reporting comes from joins. A join repeats each row on the "one" side once per matching row on the "many" side. Aggregating after that repetition counts things more than once.

Counting orders per customer after joining `order_items`:

```sql
-- Count joined lines, which repeat orders.
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
-- Independent children cross-multiply rows.
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

(Chloe and Dev, with one order and no referrals, are left out to save space.) Asha has 2 orders and 2 referrals. The join produces 2 × 2 = 4 rows for her, so both counts say 4. `COUNT(DISTINCT ...)` would happen to fix counts here, but a `SUM` cannot be repaired that way. Every value from one child table is repeated once per matching row of the other, so the sum is multiplied by that number of matches. Asha's order lines really total £142, but with her 2 referrals each line appears twice and her spend would show as £284.

`SUM(DISTINCT ...)` is no fix either: it would merge two genuinely equal values, such as two different order lines that are each worth £30.

The reliable fix is to **aggregate each relationship separately, then join the results**, using subqueries or CTEs (module 2):

```sql
-- Count each child without joining the
-- other.
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
- A count after joining lines counts lines rather than orders.
- Aggregate independent child relationships separately before joining.
- After LEFT JOIN count a right-hand key to report zero matches.

## Further reading
- [Aggregate functions — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [GROUP BY and HAVING — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-table-expressions.html)
