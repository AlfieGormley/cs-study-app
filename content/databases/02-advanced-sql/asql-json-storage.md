---
id: asql-json-storage
title: JSON storage and type choices
level: advanced
minutes: 3
summary: PostgreSQL json preserves input text; jsonb stores a decomposed representation.
sourceLesson: asql-json-upsert
---

Two features that started as vendor extensions and became everyday tools. **JSON columns** let a database table hold semi-structured data: event payloads, third-party webhooks, per-customer settings. **Upserts** ("insert, or update if it already exists") support atomic insert-or-update operations for sync jobs and counters. An additive counter is not idempotent: replaying its message increments again, so deduplicate requests when retries must not double-apply.

Both differ between SQLite and Postgres in ways that matter, so each example notes what changes.

## Storing JSON

```sql
-- Choose validated native or text JSON.
-- SQLite
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  payload TEXT NOT NULL
);
-- Postgres
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  payload jsonb NOT NULL
);
```

Four events:

```
1 {"type":"view","product":4,
   "device":{"os":"iOS"}}
2 {"type":"cart","product":4,"qty":2,
   "device":{"os":"Android"}}
3 {"type":"view","product":1,
   "tags":["sale","new"],
   "device":{"os":"iOS"}}
4 {"type":"cart","product":5,"qty":1}
```

SQLite stores JSON as ordinary text (or, since 3.45, in an internal binary form called JSONB via functions such as jsonb()). SQLite’s binary representation is private to SQLite and is not readable as PostgreSQL jsonb. A TEXT column alone does not validate JSON; a CHECK using json_valid(payload) can enforce valid text documents. PostgreSQL’s JSON types validate input.

Postgres has two types:

| | `json` | `jsonb` |
|---|---|---|
| Stored as | Exact text | Decomposed binary |
| Duplicate keys | Kept | Last wins |
| Key order | Kept | Not kept |
| Indexable (GIN) | No | Yes |
| Operators `@>`, `?` | No | Yes |

```sql
-- Choose validated native or text JSON.
SELECT '{"b":2,"a":1,"a":3}'::json,
       '{"b":2,"a":1,"a":3}'::jsonb;
-- {"b":2,"a":1,"a":3}
-- {"a": 3, "b": 2}
```

Use `jsonb` unless you must preserve the exact input text. It costs a little more on insert (JSON decoding) and avoids decoding the original input again for JSON processing; the performance difference depends on the operation and workload.

## Key takeaways
- PostgreSQL json preserves input text; jsonb stores a decomposed representation.
- SQLite JSONB and PostgreSQL jsonb are different binary representations.

## Further reading
- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: functions json](https://www.postgresql.org/docs/18/functions-json.html)
- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: sql merge](https://www.postgresql.org/docs/18/sql-merge.html)
- [SQLite reference](https://www.sqlite.org/json1.html)
