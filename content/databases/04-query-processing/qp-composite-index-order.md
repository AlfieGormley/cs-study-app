---
id: qp-composite-index-order
title: Composite indexes and skip scan
level: advanced
minutes: 3
sourceLesson: qp-index-tuning
summary: Why column order in a multi-column index decides which queries it serves well, and what PostgreSQL 18 skip scan can and cannot rescue.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

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

> [!analogy] Real-world analogy: a phone book
> A phone book is sorted by surname, then by first name. Finding every "Patel, Anita" is quick: jump to Patel, then to Anita, and the entries sit together. Finding every "Anita" whatever her surname means checking the Anitas under every surname in the book.
>
> **How it maps:** the phone book is a composite index on `(surname, first_name)`. Searching by the leading column, then the next, reads one contiguous slice. Searching only by the second column is the `(ordered_on, customer_id)` index asked for one customer: matches are scattered across every value of the leading column. Checking each surname's Anitas in turn is what skip scan does.
>
> **Where it stops:** a person can flick past a thin surname section by eye, while skip scan pays for a separate index search per leading value it tries, so it only helps when there are relatively few distinct leading values.

> [!tip] Order the columns: equality, then sort, then range
> 1. Columns compared with `=` go first.
> 2. Then the `ORDER BY` column, so rows come out in order.
> 3. Then columns compared with ranges (`<`, `>`, `BETWEEN`).
>
> Equality on leading keys and a range on the next key establish the usual scan bounds. Later conditions can still be checked within the index, and PostgreSQL 18 skip scan may perform additional searches to narrow work further. Check the actual plan rather than treating the rule as absolute.

Skip scan is usually most attractive when the omitted leading key has relatively few distinct values. PostgreSQL 18 chooses repeated searches only when its cost model expects an advantage; the exact search count need not equal the global distinct-value count, especially with LIMIT or additional bounds. In an illustrative run with 2,400 dates, a full lookup made about 2,400 descents (6.4 ms). With a million distinct leading values it would be hopeless. Design for the query; don't rely on skip scan.

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

