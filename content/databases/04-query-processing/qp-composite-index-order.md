---
id: qp-composite-index-order
title: Composite indexes and skip scan
level: advanced
minutes: 3
sourceLesson: qp-index-tuning
summary: Composite indexes and skip scan with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Composite indexes: column order is everything

A frequent query: a customer's five most recent orders.

```sql
SELECT * FROM orders
WHERE customer_id = 42
ORDER BY ordered_on DESC
LIMIT 5;
```

With an index on `(customer_id, ordered_on)`:

```
Limit  (actual rows=5.00)
-> Index Scan Backward using
     orders_cust_date_idx on orders
     Index Cond: (customer_id = 42)
     Index Searches: 1
     Buffers: shared hit=5 read=3
Execution Time: 0.032 ms
```

The index holds customer 42's entries side by side, already sorted by date. Postgres descends once, walks backwards and stops after five. There's no Sort node at all.

Now the same columns the other way round, `(ordered_on, customer_id)`:

```
Limit  (actual rows=5.00)
-> Index Scan Backward using
     orders_date_cust_idx on orders
     Index Cond: (customer_id = 42)
     Index Searches: 1031
     Buffers: shared hit=2067 read=1047
Execution Time: 3.084 ms
```

Customer 42's entries are now scattered across every date. Postgres 18's **skip scan** rescues the query by making repeated searches across date groups (1,031 illustrative searches before finding five matches). That's about 100 times slower and 390 times more buffers than the right index. Earlier PostgreSQL versions could still use the index and check the later-key condition, but without skip scan might need to read a much larger index range. Other indexes and restrictions could change the choice.

> [!tip] Order the columns: equality, then sort, then range
> 1. Columns compared with `=` go first.
> 2. Then the `ORDER BY` column, so rows come out in order.
> 3. Then columns compared with ranges (`<`, `>`, `BETWEEN`).
>
> Equality on leading keys and a range on the next key establish the usual scan bounds. Later conditions can still be checked within the index, and PostgreSQL 18 skip scan may perform additional searches to narrow work further. Check the actual plan rather than treating the rule as absolute.

Skip scan is usually most attractive when the omitted leading key has relatively few distinct values. PostgreSQL 18 chooses repeated searches only when its cost model expects an advantage; the exact search count need not equal the global distinct-value count, especially with LIMIT or additional bounds. With 2,400 dates it gave 2,400 descents for a full lookup (6.4 ms). With a million distinct leading values it would be hopeless. Design for the query; don't rely on skip scan.

## Key takeaways
- Leading equality keys followed by the desired ordering can let LIMIT stop an ordered scan early.
- PostgreSQL 18 skip scan can use repeated searches, but its usefulness depends on omitted-key distinctness and other bounds.

## Further reading
- [Multicolumn indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [Index-only scans and covering indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)
- [Partial indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-partial.html)
- [Combining multiple indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-bitmap-scans.html)
- [Operator classes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-opclass.html)
- [Use The Index, Luke: SQL indexing for developers](https://use-the-index-luke.com/)
- [Heap-only tuples (HOT) — PostgreSQL docs](https://www.postgresql.org/docs/18/storage-hot.html)

