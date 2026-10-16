---
id: asql-json-array-rows
title: Expanding arrays and building JSON results
level: advanced
minutes: 3
summary: JSON array expansion produces one result row per element.
sourceLesson: asql-json-upsert
---

events(id, payload) has four documents. Only event 3 contains tags, the array ["sale","new"]; the other documents omit tags. The shop customers and orders can also be combined into one JSON array per ordering customer.

### Arrays: one row per element

`json_each` (SQLite) and `jsonb_array_elements_text` (Postgres) are table-valued functions that expand an array into rows:

```sql
-- Expand elements into separate rows.
-- SQLite
SELECT e.id, t.value AS tag
FROM events e,
     json_each(e.payload, '$.tags') t;
-- Postgres
SELECT e.id, t.tag
FROM events e
CROSS JOIN LATERAL
  jsonb_array_elements_text(
    e.payload -> 'tags') AS t(tag);
```

Both return `(3, sale)` and `(3, new)`. Events without `tags` contribute no rows, as with an inner join.

### Building JSON

Aggregates turn rows into JSON, which is handy for APIs that want nested output in one round trip:

```sql
-- Order each customer's JSON array.
-- SQLite
SELECT c.name,
  json_group_array(o.id ORDER BY o.id)
    AS orders
FROM customers c
JOIN orders o
  ON o.customer_id = c.id
GROUP BY c.id;
-- Ana | [101,103,107]
```

Postgres uses `jsonb_agg(o.id ORDER BY o.id)` and `jsonb_build_object('name', name)`; SQLite has `json_object(...)`. To modify a document, use `json_set` (SQLite) or `jsonb_set` and the `||` merge operator (Postgres).

An inner expansion removes an event with no tags because the function yields no element rows. If the report must retain such events, PostgreSQL can use LEFT JOIN LATERAL with ON true, while SQLite can left join json_each. Check the shape before expanding: PostgreSQL jsonb_array_elements_text expects an array and errors on objects or scalar JSON values. SQLite json_each also iterates object members, so the two functions are not identical for arbitrary JSON.

The ordered SQLite aggregate shown requires SQLite 3.44 or later. Without its internal ORDER BY, [101,103,107] is merely one possible array order. PostgreSQL’s aggregate ORDER BY serves the same purpose. An outer ORDER BY sorts customer result rows and does not order the contents of an aggregate. A LEFT JOIN can produce an array containing a JSON null for an unmatched customer; filter the aggregate input if the contract requires an empty array.

## Key takeaways
- JSON array expansion produces one result row per element.
- Order JSON aggregate inputs explicitly when array order matters.

## Further reading
- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: functions json](https://www.postgresql.org/docs/18/functions-json.html)
- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: sql merge](https://www.postgresql.org/docs/18/sql-merge.html)
- [SQLite reference](https://www.sqlite.org/json1.html)
