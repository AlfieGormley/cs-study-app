---
id: asql-atomic-upserts
title: Atomic upserts, conditions and RETURNING
level: advanced
minutes: 3
summary: ON CONFLICT combines insert-or-update through a unique key.
sourceLesson: asql-json-upsert
---

stock(product_id PRIMARY KEY, qty) initially holds product 1 with 10 and product 4 with 3. Each example starts afresh from its stated initial rows. An additive stock adjustment needs request deduplication if replaying a message must have no extra effect.

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
-- Resolve a unique-key race atomically.
INSERT INTO stock (product_id, qty)
VALUES (1, 5), (2, 7)
ON CONFLICT (product_id)
DO UPDATE SET
  qty = stock.qty + excluded.qty;
```

Inside `DO UPDATE`, **`excluded`** (the *excluded row*) is the row you tried to insert, and the table name refers to the existing row. So the `SET` line computes:

```formula
q_new = q_stock + q_excluded
q_new = 10 + 5 = 15
where
q_new: the quantity stored after the upsert
q_stock: the existing row's quantity, stock.qty, here 10 for product 1
q_excluded: the quantity in the row you tried to insert, excluded.qty, here 5
In words: when the product already exists, add the incoming quantity to the stored one instead of overwriting it.
```

Starting from `(1, 10)` and `(4, 3)`, product 1 already exists, so it becomes 15. Product 2 is new and is inserted with 7, and product 4 is untouched.

Useful variations:

```sql
-- Resolve a unique-key race atomically.
-- Ignore duplicates
ON CONFLICT DO NOTHING

-- Update only if quantity is larger
ON CONFLICT (product_id)
DO UPDATE SET qty = excluded.qty
WHERE excluded.qty > stock.qty
```

Add `RETURNING *` (Postgres, SQLite 3.35+) to get the resulting rows back. When the `WHERE` rejects the update, no row is returned.

For DO UPDATE, the conflict target must match an eligible **non-deferrable unique index or constraint**. PostgreSQL exclusion constraints cannot arbitrate DO UPDATE. `ON CONFLICT (qty)` with no unique index on `qty` fails in Postgres with `there is no unique or exclusion constraint matching the ON CONFLICT specification`.

## Key takeaways
- ON CONFLICT combines insert-or-update through a unique key.
- The proposed excluded row and existing target row have different meanings.

## Further reading
- [PostgreSQL 18: datatype json](https://www.postgresql.org/docs/18/datatype-json.html)
- [PostgreSQL 18: functions json](https://www.postgresql.org/docs/18/functions-json.html)
- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: sql merge](https://www.postgresql.org/docs/18/sql-merge.html)
- [SQLite reference](https://www.sqlite.org/json1.html)
