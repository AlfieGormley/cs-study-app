---
id: asql-correlated-subqueries
title: Correlation and counting missing matches
level: basic
minutes: 3
summary: A correlated subquery binds an inner expression to a row of the enclosing query; aliases make the binding clear.
sourceLesson: asql-subqueries
---

The shop has Ana with orders 120, 60 and 60; Ben with 45 and 90; Cat with 200 and 30; Dev with 45; Eve with none. Order dates are ISO dates in 2026, with each customer’s latest dates shown below.

## Correlated subqueries

A **correlated** subquery refers to a column of the outer query. Its result is defined relative to the current row of the enclosing query, with that row’s values plugged in. This does not guarantee a separate physical execution for each row: an optimiser may rewrite the query.

Each customer's most recent order:

```sql
-- Bind matching orders to this customer.
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

> [!analogy] Real-world analogy: checking each pupil against their own class
> A teacher goes down a list of pupils from several classes. For each pupil they ask, "Is this the best mark in *this pupil's* class?", and look only at that class's marks to answer.
>
> **How it maps:** The pupil list is the outer query and the current pupil is the row of the outer query being checked. The question about "this pupil's class" is the correlated subquery: `o2.customer_id = o.customer_id` plugs the current row's customer into the inner query, just as the teacher plugs in the pupil's class.
>
> **Where it stops:** A teacher would naturally work out each class's best mark once and reuse it. SQL defines the answer for each row of the outer query but does not promise any particular method; the optimiser may rewrite the query that way. And unlike the teacher, SQL cannot guess which "class" you meant: an unqualified column name binds to the nearest table, as the next paragraph shows.

The aliases `o` and `o2` are essential. Without them, `customer_id = customer_id` inside the subquery would refer to orders inside the subquery on both sides and be true for every row.

### Correlated subqueries in SELECT

```sql
-- Bind matching orders to this customer.
SELECT c.name,
  (SELECT COUNT(*)
   FROM orders o
   WHERE o.customer_id = c.id) AS n
FROM customers c;
```

This returns Ana 3, Ben 2, Cat 2, Dev 1 and **Eve 0**. `COUNT(*)` over zero rows is 0, so customers with no orders still appear. An equivalent `LEFT JOIN ... GROUP BY` works too; the subquery form is often clearer when you want one extra figure per row.

A join rewrite needs the same empty-match behaviour. Join customers to orders with LEFT JOIN, group by the customer key and count `o.id`. Counting `*` instead counts Eve’s padded row as one. An inner join omits her entirely. These are changes in meaning, even if an execution plan happens to be cheaper.

## Key takeaways
- A correlated subquery binds an inner expression to a row of the enclosing query; aliases make the binding clear.
- COUNT(*) inside a scalar aggregate yields zero when no orders match.

## Further reading
- [PostgreSQL 18: functions subquery](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PostgreSQL 18: sql expressions](https://www.postgresql.org/docs/18/sql-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_expr.html)
