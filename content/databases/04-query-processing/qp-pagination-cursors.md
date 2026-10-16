---
id: qp-pagination-cursors
title: OFFSET and stable keyset cursors
level: advanced
minutes: 3
sourceLesson: qp-anti-patterns
summary: OFFSET and stable keyset cursors with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## 4. OFFSET pagination

```sql
-- Skipped rows must still be produced.
SELECT * FROM orders
ORDER BY id
LIMIT 20 OFFSET 900000;
```

```
Limit  (actual rows=20.00)
-> Index Scan using orders_pkey
     (actual rows=900020.00)
Execution Time: 66.979 ms
```

To skip 900,000 rows, Postgres has to produce them: it walked 900,020 index entries and fetched their rows, then threw away all but 20.

```formula
n_read = n_off + n_lim
n_read = 900,000 + 20 = 900,020
where
n_read: the number of index entries walked and rows fetched to answer one page
n_off: the OFFSET value: the number of rows skipped, here 900,000
n_lim: the LIMIT value: the number of rows returned, here 20
In words: an OFFSET query does the work of every page before the one you asked for, plus the page itself.
```

With 20 rows per page, an offset of 900,000 is page 45,001. Page 1 reads 20 rows; page 45,001 reads 900,020. The work grows in step with the page number, so the deeper users go the worse it gets.

**Keyset pagination** remembers where the last page ended:

```sql
-- Continue after the last unique ID.
SELECT * FROM orders
WHERE id > 900000   -- last id seen
ORDER BY id
LIMIT 20;
```

```
Limit  (actual rows=20.00)
-> Index Scan using orders_pkey
     Index Cond: (id > 900000)
Execution Time: 0.014 ms
```

In these illustrative timings the difference is large. Keyset pagination avoids work that grows with the skipped offset, though actual latency still depends on the data, index and system state. For a non-unique sort column, use a tie-breaker: `WHERE (ordered_on, id) < ($1, $2) ORDER BY ordered_on DESC, id DESC`. The trade-off is that you can't jump straight to page 371, which most interfaces don't need.

## Key takeaways
- OFFSET produces and discards skipped rows; keyset pagination seeks from the previous cursor.
- Use a unique ordering and match its directions and NULL handling; concurrent changes still require a consistency policy.

## Further reading
- [Sargable — Wikipedia](https://en.wikipedia.org/wiki/Sargable)
- [Use The Index, Luke: functions in WHERE clauses](https://use-the-index-luke.com/sql/where-clause/functions)
- [Use The Index, Luke: paging through results without OFFSET](https://use-the-index-luke.com/no-offset)
- [Don't Do This — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Subquery expressions (EXISTS, IN, NOT IN) — PostgreSQL docs](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PREPARE and plan_cache_mode — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-prepare.html)
- [Slow counting — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Slow_Counting)
- [WITH queries (CTEs) — PostgreSQL docs](https://www.postgresql.org/docs/18/queries-with.html)

