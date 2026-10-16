---
id: asql-upsert-batch-replace
title: Duplicate batch keys and replacement deletes
level: advanced
minutes: 3
summary: PostgreSQL DO UPDATE cannot affect the same target row twice in one command.
sourceLesson: asql-json-upsert
---

stock(product_id PRIMARY KEY, qty, note) tracks quantity and an optional note. PostgreSQL and SQLite share ON CONFLICT syntax but differ when one input batch repeats a key. Each example is isolated from the others.

### Duplicate keys in one statement

```sql
-- Test this batch in isolation.
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
-- Test this batch in isolation.
-- before: (4, 3, 'warehouse')
INSERT OR REPLACE INTO stock
  (product_id, qty) VALUES (4, 8);
-- after:  (4, 8, NULL)
```

The `note` column was lost because the new row didn't supply it. In SQLite, delete triggers fire for that deletion only if recursive triggers are enabled, and foreign keys with `ON DELETE CASCADE` can remove child rows. Use `ON CONFLICT ... DO UPDATE` to change only the columns you name.

A related SQLite parsing quirk: in `INSERT ... SELECT ... FROM t ON CONFLICT ...`, the parser reads `ON` as a join condition on `t` and fails with `near "DO": syntax error`. Give the `SELECT` a `WHERE` clause (even `WHERE true`) to fix it.

## Key takeaways
- PostgreSQL DO UPDATE cannot affect the same target row twice in one command.
- SQLite REPLACE deletes the old row and inserts a new one.

## Further reading
- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: functions json](https://www.postgresql.org/docs/18/functions-json.html)
- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: sql merge](https://www.postgresql.org/docs/18/sql-merge.html)
- [SQLite reference](https://www.sqlite.org/json1.html)
