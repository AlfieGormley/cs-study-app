---
id: qp-expression-pattern-indexes
title: Expressions, patterns and bitmap combinations
level: advanced
minutes: 3
sourceLesson: qp-index-tuning
summary: How expression indexes and operator classes let an index match lower(), LIKE prefixes and other non-plain conditions, and how bitmaps combine indexes.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Expression indexes and operator classes

An index on `email` does not directly search the lower-case expression in `WHERE lower(email) = ...`, because the index stores `email`, not `lower(email)`. Index the expression:

```sql
-- Store lower-case values as search keys.
CREATE INDEX customers_lower_email_idx
  ON customers (lower(email));
```

| Index | Plan | Time |
|---|---|---|
| None | Seq Scan, 99,999 removed | 17 ms |
| On `lower(email)` | Index Scan | 0.02 ms |

For the simple equality shown, an ordinary email index cannot supply a selective lower-case-expression lookup. It can still be scanned as a covering path in some queries; a function does not make every use of an index impossible.

ANALYZE also gathers statistics on indexed expressions, so the row estimate improves from the 0.5% default (500) to 1.

Pattern planning also depends on the collation and operator. These examples assume a deterministic collation; PostgreSQL 18 supports LIKE with some nondeterministic collations, but index support still needs checking for the specific expression and pattern.

**Operator classes** matter for `LIKE`. In a database whose collation isn't `C`, a plain B-tree on a text column can't serve `LIKE 'abc%'`, because the collation's sort order doesn't keep prefixes together byte-wise. An index built with `text_pattern_ops` can:

```sql
-- Use byte-order keys for LIKE prefixes.
CREATE INDEX customers_email_pattern_idx
  ON customers (email text_pattern_ops);
```

A pattern beginning with a wildcard such as `LIKE '%abc'` supplies no selective prefix range for an ordinary B-tree. A full or index-only scan can still use that index as a covering access path. For indexed substring search, consider a trigram index (`pg_trgm` with GIN or GiST).

## Combining indexes

Postgres can combine single-column indexes with bitmaps:

```
Bitmap Heap Scan on orders
  (actual rows=308.00)
-> BitmapAnd
   -> Bitmap Index Scan
        on orders_cust_cov_idx
        Index Cond: (customer_id < 500)
        (actual rows=4984.00)
   -> Bitmap Index Scan on orders_date_idx
        Index Cond:
          (ordered_on < '2020-06-01')
        (actual rows=63535.00)
Execution Time: 2.148 ms
```

It read 4,984 and 63,535 index entries to find 308 rows. A suitable composite index may reduce the work for this exact query, but bitmap combination means a few well-chosen single-column indexes can serve many query shapes reasonably. That's often the better trade when queries are ad hoc.

## Key takeaways
- Match an expression index to the expression searched, and check collation and operator-class requirements for prefixes.
- Bitmap combinations can serve varied predicates but do not preserve B-tree ordering.

## Further reading
- [Multicolumn indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [Index-only scans and covering indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)
- [Partial indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-partial.html)
- [Combining multiple indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-bitmap-scans.html)
- [Operator classes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-opclass.html)
- [Use The Index, Luke: SQL indexing for developers](https://use-the-index-luke.com/)
- [Heap-only tuples (HOT) — PostgreSQL docs](https://www.postgresql.org/docs/18/storage-hot.html)

