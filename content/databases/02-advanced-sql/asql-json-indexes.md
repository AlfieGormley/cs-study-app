---
id: asql-json-indexes
title: Indexing JSON and promoting stable keys
level: advanced
minutes: 3
summary: An expression index targets a selected JSON expression.
sourceLesson: asql-json-upsert
---

events(id, payload jsonb) contains view events 1 and 3 and cart events 2 and 4. Only event 3 has a tags key. An index is an additional search structure; it changes access cost rather than the meaning of a query.

## Indexing JSON in Postgres

Without a suitable access path, a JSON predicate may require scanning many rows. PostgreSQL jsonb is already decoded; a scan does not reparse the original JSON text, and other indexed predicates may narrow the rows first. Two options:

**Expression index** on one frequently queried JSON key:

```sql
-- Match the predicate to its index.
CREATE INDEX events_type_idx
ON events ((payload ->> 'type'));
```

The query must use a matching expression that the planner recognises (`payload ->> 'type' = 'cart'`). SQLite supports the same idea with indexes on expressions.

**GIN index** for containment and key-existence queries:

```sql
-- Match the predicate to its index.
CREATE INDEX events_gin
ON events USING gin (payload);

SELECT id FROM events
WHERE payload @> '{"type":"cart"}';
-- 2, 4
```

> [!analogy] Real-world analogy: a bookmark tab versus a book's index
> A reference book can have coloured tabs for one chapter you use constantly, or an index at the back listing every term and the pages it appears on.
>
> **How it maps:** The expression index is the tab: it covers one chosen expression, `payload ->> 'type'`, and serves queries that use exactly that expression. The GIN index is the back-of-book index: it records the keys and values inside every document, so a containment query such as `@>` can look up which rows contain them.
>
> **Where it stops:** A book index helps any reader looking up a word. A GIN index helps only the operators its operator class supports, and the planner may still choose a scan when the table is small or the filter matches many rows.

`@>` means "contains this sub-document" and `?` means "has this top-level key". A default GIN index on `jsonb` supports `@>`, `?`, `?|` and `?&`. The `jsonb_path_ops` operator class often yields a smaller and more selective index, depending on the documents and query. It supports @>, @? and @@ but not the key-existence operators. The default jsonb_ops class supports those JSON path operators too. Index support means the predicate is eligible for that access path; a small table or unselective filter can still favour a scan.

> [!warning] When JSON is the wrong tool
> If every row has the same keys and you filter, join or aggregate on them, they should be **columns**. Columns get types, `NOT NULL` and foreign keys, ordinary column statistics, and a deliberately chosen scalar representation. JSON shines for genuinely variable data you mostly store and return whole. A common pattern is promoting a frequently queried JSON key to a generated column.

## Key takeaways
- An expression index targets a selected JSON expression.
- GIN operator classes support different JSON predicates.

## Further reading
- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: functions json](https://www.postgresql.org/docs/18/functions-json.html)
- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: sql merge](https://www.postgresql.org/docs/18/sql-merge.html)
- [SQLite reference](https://www.sqlite.org/json1.html)
