---
id: asql-json-extraction
title: JSON extraction and numeric comparisons
level: advanced
minutes: 3
summary: PostgreSQL ->> returns text; cast before numerical comparisons.
sourceLesson: asql-json-upsert
---

events(id, payload) contains JSON documents. Event 1 is a view of product 4 on iOS; event 2 is a cart for product 4, qty 2, on Android; event 3 is a view of product 1 on iOS with tags sale and new; event 4 is a cart for product 5 with qty 1 and no device key.

## Reading values

Both databases spell extraction with arrows, but the details differ:

| | SQLite | Postgres |
|---|---|---|
| `->` | JSON text | `jsonb` |
| `->>` | SQL value | `text` |
| Path | `'$.device.os'` | `-> 'device' ->> 'os'` |

```sql
-- Extract first; cast numeric text.
-- SQLite
SELECT id,
  payload ->> '$.type' AS type,
  payload ->> '$.device.os' AS os
FROM events;
-- Postgres
SELECT id,
  payload ->> 'type' AS type,
  payload #>> '{device,os}' AS os
FROM events;
```

| id | type | os |
|---|---|---|
| 1 | view | iOS |
| 2 | cart | Android |
| 3 | view | iOS |
| 4 | cart | NULL |

A missing key gives NULL, not an error. That is convenient, but it also means a typo in a key name silently returns NULL everywhere.

### The type trap

In SQLite, `->>` returns a native SQL value: `payload ->> '$.qty'` is the **integer** 2. In Postgres, `->>` always returns **text**:

```sql
-- Extract first; cast numeric text.
-- Postgres
WHERE payload ->> 'qty' > 1
-- ERROR: operator does not exist:
--        text > integer

WHERE payload ->> 'qty' > '10'
-- matches qty 2 under C collation

WHERE (payload ->> 'qty')::int > 1
-- correct
```

For the demonstrated lexicographic ordering assume C collation. The second form is the dangerous one: it runs, and compares strings character by character. Cast before comparing numbers or dates, and validate incoming shapes: a non-numeric string will make an integer cast fail rather than silently become a number. PostgreSQL -> returns json when the input is json and jsonb when it is jsonb; the table above assumes the payload is jsonb. JSON null is distinct from a missing key when using ->, but ->> turns either into SQL NULL. SQLite ->> also returns 1 or 0 for JSON true or false.

## Key takeaways
- PostgreSQL ->> returns text; cast before numerical comparisons.
- SQLite ->> can return an integer, real, text or NULL SQL value.

## Further reading
- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: functions json](https://www.postgresql.org/docs/18/functions-json.html)
- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: sql merge](https://www.postgresql.org/docs/18/sql-merge.html)
- [SQLite reference](https://www.sqlite.org/json1.html)
