---
id: asql-merge-concurrency
title: MERGE actions, concurrency and returned row versions
level: advanced
minutes: 3
summary: MERGE chooses the first applicable WHEN clause for each candidate row.
sourceLesson: asql-json-upsert
---

stock(product_id PRIMARY KEY, qty) starts with product 1 at 15 for the MERGE example. PostgreSQL 15 introduced MERGE; version 17 added its RETURNING clause, and version 18 added `old` and `new` row references to RETURNING for INSERT, UPDATE, DELETE and MERGE.

### MERGE (Postgres 15+)

The SQL-standard `MERGE` handles matched and unmatched rows with separate actions, including deletes:

```sql
-- First applicable action wins.
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

The first `WHEN MATCHED` clause tests the quantity the row would end up with: if applying the change would leave zero or less in stock, it deletes the row instead of updating it. Product 1 (qty 15) would drop to 0, so it is deleted; product 3 has no match and is inserted with 4. MERGE tries the WHEN clauses in order and uses the first one whose condition is true, which is why the DELETE clause comes before the plain UPDATE. Postgres 17 added `RETURNING` with `merge_action()` to report which branch each row took. SQLite has no `MERGE`.

Prefer `ON CONFLICT` for concurrent upserts in Postgres. It is built on the unique index and, in the absence of independent errors, resolves a concurrent conflict by inserting or updating (unless an update WHERE rejects the row). Other constraints, deadlocks or serialization failures can still raise errors that the application must handle or retry. `MERGE` joins first and can still fail with a unique violation if another transaction inserts the same key concurrently.

### Other upsert details

- **SQL sequences still advance.** In Postgres, an insert that ends in `DO UPDATE` or `DO NOTHING` has usually already taken a `serial`/identity value, so ids get gaps. That is normal; don't rely on contiguous ids.
- **Inserted or updated?** Postgres users often test `xmax = 0` in `RETURNING`, but that relies on an internal system column. Postgres 18 adds `RETURNING old.*, new.*`; the `old` values are all NULL when the row was freshly inserted, which is the supported way to tell.

## Key takeaways
- MERGE chooses the first applicable WHEN clause for each candidate row.
- Use ON CONFLICT for PostgreSQL concurrent upserts and handle independent transaction errors.

## Further reading
- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: functions json](https://www.postgresql.org/docs/18/functions-json.html)
- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: sql merge](https://www.postgresql.org/docs/18/sql-merge.html)
- [SQLite reference](https://www.sqlite.org/json1.html)
