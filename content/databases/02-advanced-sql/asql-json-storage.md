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

> [!analogy] Real-world analogy: a photocopy versus a typed-up record
> An office receives handwritten forms. It can file a photocopy of each form exactly as written, or type the answers into its records system, one field per box.
>
> **How it maps:** `json` is the photocopy: the exact text, spacing, key order and any repeated keys are kept, and every lookup has to read the original again. `jsonb` is the typed-up record: decomposed into keys and values, so lookups and indexes work on fields directly. If a form answered the same question twice, the typed record keeps only the last answer, just as jsonb keeps the last duplicate key.
>
> **Where it stops:** A clerk may mistype; jsonb keeps the JSON values themselves (strings, numbers, booleans, nulls), though it may rewrite how a value is spelled: `1.230e-5` comes back as `0.00001230`. What it does not keep is the original text: whitespace, key order and all but the last of any duplicate keys.

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
