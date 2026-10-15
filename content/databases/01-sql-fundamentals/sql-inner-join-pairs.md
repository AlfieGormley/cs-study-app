---
id: sql-inner-join-pairs
title: Trace matching pairs in an inner join
level: basic
minutes: 4
sourceLesson: sql-joins
summary: An inner join returns one row per matching pair.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

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
-- Each matching customer/order pair
-- survives.
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

## Key takeaways
- An inner join returns one row per matching pair.
- Asha appears twice because she has two orders.
- Qualify shared names with table aliases.

## Further reading
- [Joins between tables — PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial-join.html)
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
