---
id: qp-subquery-semantics
title: Exclusion, existence and repeated subqueries
level: advanced
minutes: 5
sourceLesson: qp-anti-patterns
summary: Exclusion, existence and repeated subqueries with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## 5. NOT IN with a subquery

```sql
-- NULLs can change NOT IN semantics.
SELECT count(*) FROM customers c
WHERE c.id NOT IN
  (SELECT customer_id FROM orders
   WHERE status = 'pending');
```

`NOT IN` has two problems.

**Semantics.** If the subquery returns even one NULL, `x NOT IN (...)` is never true (it's NULL or false), so no customer rows satisfy the filter. This `count(*)` query still returns one result row containing 0. That is almost never the intended count.

**Performance.** For this PostgreSQL 18 subquery form, the plan commonly uses a SubPlan rather than an ordinary anti-join. It runs the subquery once and probes a hash table of its results (`hashed SubPlan`), which was fine here: 17 ms. But if the subquery's estimated results exceed the applicable hash-memory budget, the plan becomes a plain SubPlan that rescans the retained subquery results for **every** outer row. With `work_mem` reduced to 64 kB the estimated cost jumped from about 10,700 to 976 million.

For exclusion by absence of an equal key, this simple `NOT EXISTS` form can become an anti-join:

```sql
-- Exclude by absence of an equal key.
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.id
    AND o.status = 'pending')
```

```
Hash Right Anti Join
  Hash Cond: (o.customer_id = c.id)
Execution Time: 22.855 ms
```

Here it was slightly slower than the hashed `NOT IN`, but it permits anti-join strategies and avoids this particular NULL trap. It can still be slow for other reasons, and it intentionally differs from NOT IN for NULLs, including NULL outer keys.

## 6. Correlated subqueries: a nested loop in disguise

```sql
-- Count orders separately per customer.
SELECT c.id,
  (SELECT count(*) FROM orders o
   WHERE o.customer_id = c.id)
FROM customers c
WHERE c.city = 'York';
```

Postgres runs a scalar subquery in the SELECT list once **per outer row**:

```
Seq Scan on customers c
  (actual rows=12500.00)
  SubPlan 1
  -> Aggregate (loops=12500)
     -> Index Only Scan using
          orders_cust_cov_idx
          (loops=12500)
Execution Time: 30.428 ms
```

That's a nested loop over 12,500 customers. With an index on `orders(customer_id)` each loop is cheap and the whole thing took 30 ms. The equivalent `LEFT JOIN ... GROUP BY` actually took 84 ms here, because it hashed all 1,000,000 orders.

So correlated subqueries aren't always slow, but they are only as fast as the inner lookup. Without the index, each of the 12,500 loops would be a full scan of `orders`: an estimated cost of about 248 million, against 23,000 for the join. Check `loops` on any SubPlan.

## 7. DISTINCT to hide duplicate rows

"Customers in Bath who have ordered" written as a join returns one row per order, so people add DISTINCT:

```sql
-- The join can multiply customer rows.
SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE c.city = 'Bath';
```

The join produced 125,174 rows, then a HashAggregate collapsed them back to 12,500: 42 ms. The question was really "does at least one order exist?", which is a semi-join:

```sql
-- Existence returns each customer once.
SELECT c.* FROM customers c
WHERE c.city = 'Bath'
  AND EXISTS (SELECT 1 FROM orders o
              WHERE o.customer_id = c.id);
```

```
Nested Loop Semi Join
  (actual rows=12500.00)
Execution Time: 10.958 ms
```

Four times faster: the semi-join stops at each customer's first order instead of producing all ten and de-duplicating. A `DISTINCT` you added to fix duplicates is a sign the query asks the wrong question.

## Aggregating before a join

A third formulation counts orders once, then joins those counts to customers:

```sql
-- One result row per customer key.
SELECT c.id, coalesce(x.n, 0) AS n
FROM customers c
LEFT JOIN (
  SELECT customer_id, count(*) AS n
  FROM orders GROUP BY customer_id
) x ON x.customer_id = c.id
WHERE c.city = 'York';
```

The left join retains customers with no orders; `coalesce` gives them zero. With a direct left join, use `count(o.id)` rather than `count(*)` to avoid counting the NULL-extended unmatched row. This formulation may scan and aggregate every order, while the scalar subquery can make just the indexed customer lookups needed by a selective outer filter.

Early aggregation can reduce intermediate rows, but moving it across joins must preserve grouping keys, duplicate multiplicities, NULL behaviour and the requested aggregate. Joining order counts to several item rows and then summing can multiply those counts. Combining partial averages requires their sums and counts, rather than an unweighted average of averages. Compare equivalent answers before comparing plans.

## Key takeaways
- NOT IN and NOT EXISTS differ when NULLs are involved; use the intended semantics.
- A scalar correlated lookup may be efficient with a selective index; EXISTS avoids unnecessary join multiplicity when only existence is needed.

## Further reading
- [Database System Concepts: query processing and partial aggregation](https://www.db-book.com/slides-dir/PDF-dir/ch15.pdf)
- [Sargable — Wikipedia](https://en.wikipedia.org/wiki/Sargable)
- [Use The Index, Luke: functions in WHERE clauses](https://use-the-index-luke.com/sql/where-clause/functions)
- [Use The Index, Luke: paging through results without OFFSET](https://use-the-index-luke.com/no-offset)
- [Don't Do This — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Subquery expressions (EXISTS, IN, NOT IN) — PostgreSQL docs](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PREPARE and plan_cache_mode — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-prepare.html)
- [Slow counting — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Slow_Counting)
- [WITH queries (CTEs) — PostgreSQL docs](https://www.postgresql.org/docs/18/queries-with.html)

