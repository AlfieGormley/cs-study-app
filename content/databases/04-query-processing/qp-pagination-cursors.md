---
id: qp-pagination-cursors
title: OFFSET and stable keyset cursors
level: advanced
minutes: 3
sourceLesson: qp-anti-patterns
summary: Why OFFSET pagination gets slower the deeper you page, and how keyset pagination with a unique cursor avoids it.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

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

To skip 900,000 rows, Postgres has to produce them: it walked 900,020 index entries and fetched their rows, then threw away all but 20. An OFFSET query does the work of every page before the one you asked for, plus the page itself.

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

> [!analogy] Real-world analogy: a bookmark
> To carry on reading a novel, you can count pages from the front until you reach page 371, or open it at your bookmark. Counting gets slower the further through the book you are; the bookmark takes the same moment on page 3 or page 371.
>
> **How it maps:** counting from the front is OFFSET, which produces and discards every earlier row. The bookmark is the keyset cursor: the last `id` (or last sort values) seen, from which the index can seek straight to the next row.
>
> **Where it stops:** a book's pages never move, but rows can be inserted or deleted between requests, so a cursor continues after a value rather than at a fixed position, and the next page reflects whatever changed in between.

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

