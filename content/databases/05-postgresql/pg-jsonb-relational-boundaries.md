---
id: pg-jsonb-relational-boundaries
title: JSONB alongside relational columns
level: intermediate
minutes: 2
sourceLesson: postgresql-in-practice
summary: Keep required keys and relationships in constrained columns.
---

The ticket-shop `events` table has `name text NOT NULL` and `details jsonb NOT NULL DEFAULT '{}'`, alongside its identity, availability and start-time columns. The schema unit inserts a workshop with `{ "format": "online" }` in `details`. Run the following queries after that ticket-shop fixture setup.

## Keep important rules explicit

Use relational columns for important keys, relationships and invariants. Use JSONB for attributes that genuinely vary, such as event presentation settings.

```sql
-- Match a contained key/value pair.
SELECT name
FROM events
WHERE details @> '{"format":"online"}';

-- GIN can index containment searches.
CREATE INDEX events_details_gin
ON events USING gin (details);
```

The containment operator `@>` can use this GIN index for selective queries at sufficient scale. JSONB stores a processed representation rather than preserving input whitespace and key order. Duplicate object keys do not remain separate entries. Use `json` instead if preserving the input text matters more than JSONB's processing and indexing advantages.

A JSON document does not automatically enforce the types and relationships your application expects. If every event has a required capacity used in constraints and joins, a typed column is usually easier to validate and optimise than hiding it in JSON. Large document updates also carry write and index maintenance costs.

## Key takeaways

- Keep required keys and relationships in constrained columns.
- GIN can support selective JSONB containment queries.
- JSONB does not preserve input text or duplicate keys.

## Further reading

- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: gin intro](https://www.postgresql.org/docs/18/gin.html)
- [PostgreSQL 18: indexes types](https://www.postgresql.org/docs/18/indexes-types.html)
