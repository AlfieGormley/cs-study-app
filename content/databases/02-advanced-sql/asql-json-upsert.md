---
id: asql-json-upsert
title: JSON in SQL, upserts
level: advanced
minutes: 15
summary: Storing and querying JSON in SQLite and PostgreSQL (json vs jsonb, operators, GIN and expression indexes), then atomic insert-or-update with ON CONFLICT, MERGE and RETURNING, and the traps in each.
---

Two features that started as vendor extensions and became everyday tools. **JSON columns** let a relational table hold semi-structured data: event payloads, third-party webhooks, per-customer settings. **Upserts** ("insert, or update if it already exists") support atomic insert-or-update operations for sync jobs and counters. An additive counter is not idempotent: replaying its message increments again, so deduplicate requests when retries must not double-apply.

Both differ between SQLite and Postgres in ways that matter, so each example notes what changes.

## Storing JSON

```sql
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

SQLite stores JSON as ordinary text (or, since 3.45, in an internal binary form called JSONB via the `jsonb()` functions). Postgres has two types:

| | `json` | `jsonb` |
|---|---|---|
| Stored as | Exact text | Parsed binary |
| Duplicate keys | Kept | Last wins |
| Key order | Kept | Not kept |
| Indexable (GIN) | No | Yes |
| Operators `@>`, `?` | No | Yes |

```sql
SELECT '{"b":2,"a":1,"a":3}'::json,
       '{"b":2,"a":1,"a":3}'::jsonb;
-- {"b":2,"a":1,"a":3}
-- {"a": 3, "b": 2}
```

Use `jsonb` unless you must preserve the exact input text. It costs a little more on insert (parsing) and avoids reparsing for JSON processing; the performance difference depends on the operation and workload.

## Reading values

Both databases spell extraction with arrows, but the details differ:

| | SQLite | Postgres |
|---|---|---|
| `->` | JSON text | `jsonb` |
| `->>` | SQL value | `text` |
| Path | `'$.device.os'` | `-> 'device' ->> 'os'` |

```sql
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
-- Postgres
WHERE payload ->> 'qty' > 1
-- ERROR: operator does not exist:
--        text > integer

WHERE payload ->> 'qty' > '10'
-- matches qty 2 ('2' > '10' as text)

WHERE (payload ->> 'qty')::int > 1
-- correct
```

The second form is the dangerous one: it runs, and compares strings character by character. Always cast before comparing numbers or dates.

### Arrays: one row per element

`json_each` (SQLite) and `jsonb_array_elements_text` (Postgres) are table-valued functions that expand an array into rows:

```sql
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
-- SQLite
SELECT c.name,
  json_group_array(o.id) AS orders
FROM customers c
JOIN orders o
  ON o.customer_id = c.id
GROUP BY c.id;
-- Ana | [101,103,107]
```

Postgres uses `jsonb_agg(o.id ORDER BY o.id)` and `jsonb_build_object('name', name)`; SQLite has `json_object(...)`. To modify a document, use `json_set` (SQLite) or `jsonb_set` and the `||` merge operator (Postgres).

## Indexing JSON in Postgres

Without a suitable access path, a JSON predicate may require scanning many rows. PostgreSQL jsonb is already parsed; a scan does not reparse the original JSON text, and other indexed predicates may narrow the rows first. Two options:

**Expression index** on one hot key:

```sql
CREATE INDEX events_type_idx
ON events ((payload ->> 'type'));
```

The query must use the identical expression (`payload ->> 'type' = 'cart'`). SQLite supports the same idea with indexes on expressions.

**GIN index** for containment and key-existence queries:

```sql
CREATE INDEX events_gin
ON events USING gin (payload);

SELECT id FROM events
WHERE payload @> '{"type":"cart"}';
-- 2, 4
```

`@>` means "contains this sub-document" and `?` means "has this top-level key". A default GIN index on `jsonb` supports `@>`, `?`, `?|` and `?&`. The `jsonb_path_ops` operator class makes a smaller, faster index that supports only `@>` (and JSON path matches).

> [!warning] When JSON is the wrong tool
> If every row has the same keys and you filter, join or aggregate on them, they should be **columns**. Columns get types, `NOT NULL` and foreign keys, accurate planner statistics, and compact storage. JSON shines for genuinely variable data you mostly store and return whole. A common pattern is promoting a hot key to a generated column.

## Upserts

The problem: insert a stock row for a product, or add to it if the row already exists. The naive approach races:

```
T1: SELECT ... product 2 -> none
T2: SELECT ... product 2 -> none
T1: INSERT product 2      ok
T2: INSERT product 2      duplicate
                          key error
```

`INSERT ... ON CONFLICT` makes the check and the write one atomic operation. The syntax is the same in Postgres (9.5+) and SQLite (3.24+):

```sql
INSERT INTO stock (product_id, qty)
VALUES (1, 5), (2, 7)
ON CONFLICT (product_id)
DO UPDATE SET
  qty = stock.qty + excluded.qty;
```

Starting from `(1, 10)` and `(4, 3)`, product 1 already exists, so it becomes 15. Product 2 is new and is inserted with 7. Inside `DO UPDATE`, **`excluded`** is the row you tried to insert, and the table name refers to the existing row.

Useful variations:

```sql
-- Ignore duplicates
ON CONFLICT DO NOTHING

-- Update only if quantity is larger
ON CONFLICT (product_id)
DO UPDATE SET qty = excluded.qty
WHERE excluded.qty > stock.qty
```

Add `RETURNING *` (Postgres, SQLite 3.35+) to get the resulting rows back. When the `WHERE` rejects the update, no row is returned.

The conflict target must match a **unique index or constraint**. `ON CONFLICT (qty)` with no unique index on `qty` fails in Postgres with `there is no unique or exclusion constraint matching the ON CONFLICT specification`.

### Duplicate keys in one statement

```sql
INSERT INTO stock (product_id, qty)
VALUES (5, 1), (5, 2)
ON CONFLICT (product_id)
DO UPDATE SET
  qty = stock.qty + excluded.qty;
```

| Database | Result |
|---|---|
| SQLite | row 5 has qty 3 |
| Postgres | error |

Postgres refuses: `ON CONFLICT DO UPDATE command cannot affect row a second time`. Within one statement, it won't update a row it has already inserted or updated, because the outcome would depend on processing order. SQLite processes the rows one at a time, so the second updates the first. Batch loaders for Postgres must de-duplicate keys in the batch first (for example, `GROUP BY product_id` with `SUM(qty)`).

### INSERT OR REPLACE is not an upsert

SQLite also has `INSERT OR REPLACE` (and MySQL has `REPLACE`). It resolves a conflict by **deleting** the old row and inserting a new one:

```sql
-- before: (4, 3, 'warehouse')
INSERT OR REPLACE INTO stock
  (product_id, qty) VALUES (4, 8);
-- after:  (4, 8, NULL)
```

The `note` column was lost because the new row didn't supply it. Delete triggers may fire and foreign keys with `ON DELETE CASCADE` can remove child rows. Use `ON CONFLICT ... DO UPDATE` to change only the columns you name.

A related SQLite parsing quirk: in `INSERT ... SELECT ... FROM t ON CONFLICT ...`, the parser reads `ON` as a join condition on `t` and fails with `near "DO": syntax error`. Give the `SELECT` a `WHERE` clause (even `WHERE true`) to fix it.

### MERGE (Postgres 15+)

The SQL-standard `MERGE` handles matched and unmatched rows with separate actions, including deletes:

```sql
MERGE INTO stock s
USING (VALUES (1, -15), (3, 4))
  AS v(pid, delta)
ON s.product_id = v.pid
WHEN MATCHED
  AND s.qty + v.delta <= 0
  THEN DELETE
WHEN MATCHED THEN
  UPDATE SET qty = s.qty + v.delta
WHEN NOT MATCHED THEN
  INSERT (product_id, qty)
  VALUES (v.pid, v.delta);
```

Product 1 (qty 15) would drop to 0, so it is deleted; product 3 is inserted. Postgres 17 added `RETURNING` with `merge_action()` to report which branch each row took. SQLite has no `MERGE`.

Prefer `ON CONFLICT` for concurrent upserts in Postgres. It is built on the unique index and, in the absence of independent errors, resolves a concurrent conflict by inserting or updating (unless an update WHERE rejects the row). Other constraints, deadlocks or serialization failures can still require error handling or retries. `MERGE` joins first and can still fail with a unique violation if another transaction inserts the same key concurrently.

### Other upsert details

- **Sequences still advance.** In Postgres, an insert that ends in `DO UPDATE` or `DO NOTHING` has usually already taken a `serial`/identity value, so ids get gaps. That is normal; don't rely on contiguous ids.
- **Inserted or updated?** Postgres users often test `xmax = 0` in `RETURNING`, but that relies on an internal system column. Postgres 18 adds `RETURNING old.*, new.*`; the `old` values are all NULL when the row was freshly inserted, which is the supported way to tell.

## Key takeaways
- In Postgres prefer `jsonb`: parsed once, indexable with GIN, with containment (`@>`) and key (`?`) operators.
- SQLite's `->>` returns typed SQL values; Postgres's `->>` returns text, so cast before numeric comparisons.
- Index the JSON keys you filter on (expression or GIN index), and promote stable, hot keys to real columns.
- `INSERT ... ON CONFLICT (key) DO UPDATE` is an atomic upsert in both databases; `excluded` is the proposed row.
- Postgres rejects a single upsert that touches the same key twice; SQLite applies them in order.
- `INSERT OR REPLACE` deletes then inserts, losing unspecified columns; `MERGE` (Postgres 15+) adds conditional deletes but isn't a concurrency-safe upsert.

## Further reading
- [JSON types — PostgreSQL docs](https://www.postgresql.org/docs/current/datatype-json.html)
- [JSON functions and operators — PostgreSQL docs](https://www.postgresql.org/docs/current/functions-json.html)
- [JSON functions — SQLite docs](https://www.sqlite.org/json1.html)
- [UPSERT — SQLite docs](https://www.sqlite.org/lang_upsert.html)
- [INSERT (ON CONFLICT) — PostgreSQL docs](https://www.postgresql.org/docs/current/sql-insert.html)
- [MERGE — PostgreSQL docs](https://www.postgresql.org/docs/current/sql-merge.html)
