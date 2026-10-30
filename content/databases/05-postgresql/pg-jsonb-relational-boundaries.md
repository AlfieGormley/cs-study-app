---
id: pg-jsonb-relational-boundaries
title: JSONB alongside relational columns
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: Keep required values and relationships in typed columns, and use JSONB for attributes that genuinely vary.
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

The containment operator `@>` asks whether the document includes the given keys and values. A GIN index can serve it for selective queries at sufficient scale. In a PostgreSQL 18 test with 200,000 documents, a search matching 200 of them used the GIN index, while a search matching almost every row ignored it and scanned the table. An ordinary B-tree index on the whole `jsonb` column does not help `@>` at all, because index support depends on the operator and the index method.

JSONB stores a processed representation rather than the input text. It drops insignificant whitespace, does not keep key order, and keeps only the last value for a duplicated key: `'{"a": 2, "a": 3}'::jsonb` becomes `{"a": 3}`. Use `json` instead if preserving the input text matters more than JSONB's processing and indexing advantages.

A JSON document does not automatically enforce the types and relationships your application expects. If every event has a required capacity used in constraints and joins, a typed column is usually easier to validate and optimise than hiding it in JSON. Updating one key still writes a new version of the whole row, with its write and index maintenance costs.

> [!analogy] Real-world analogy: a printed form with a notes section
> A booking form has printed boxes for name, date and number of seats, which a clerk checks before accepting it. At the bottom is a free notes section where people write whatever extra details they like.
>
> **How it maps:** the printed boxes are typed columns with `NOT NULL`, `CHECK` and foreign keys. The notes section is the JSONB column: flexible, but nobody checks that "capacity" was written there, or written as a number.
>
> **Where it stops:** handwritten notes are hard to search, whereas JSONB keeps typed JSON values that you can query and index with GIN. A notes section also keeps exactly what was written; JSONB normalises it.

## Key takeaways

- Keep required values and relationships in constrained columns.
- GIN can support selective JSONB containment queries; a plain B-tree cannot.
- JSONB drops whitespace, key order and all but the last duplicate key.

## Further reading

- [PostgreSQL 18: JSON types](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: GIN indexes](https://www.postgresql.org/docs/18/gin.html)
- [PostgreSQL 18: index types](https://www.postgresql.org/docs/18/indexes-types.html)
