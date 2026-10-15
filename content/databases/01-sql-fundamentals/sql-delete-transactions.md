---
id: sql-delete-transactions
title: Check destructive writes and roll them back
level: intermediate
minutes: 3
sourceLesson: sql-dml-constraints
summary: A DELETE removes rows; an UPDATE can clear an individual nullable value.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. Examples of writes start from that original data unless a block explicitly groups statements together.

## DELETE

```sql
-- Remove the one line belonging to order
-- 105.
DELETE FROM order_items
WHERE order_id = 105;
```

`DELETE` removes whole rows. To remove a value, `UPDATE` it to NULL instead. To empty a table quickly, `TRUNCATE` (PostgreSQL) skips per-row work, but it is all-or-nothing and doesn't fire row-level triggers. SQLite has no `TRUNCATE`; it optimises an unfiltered `DELETE FROM t` instead.

## The missing WHERE

`UPDATE products SET category = 'sale';` changes **every** product. `DELETE FROM order_items;` removes all nine order lines. Both are valid statements and can finish before you notice in this tiny shop; large tables can instead take substantial time and hold locks.

> [!warning] A safe routine for risky changes
> 1. Write the `WHERE` clause first, as a `SELECT`, and check the rows and count.
> 2. Start a transaction with `BEGIN`.
> 3. Run the `UPDATE` or `DELETE` with the same `WHERE`. Check the affected row count it reports.
> 4. `COMMIT` if it matches, `ROLLBACK` if it doesn't.

```sql
-- Undo a deletion of every original line.
BEGIN;
DELETE FROM order_items;
-- 9 rows: that's all of them!
ROLLBACK;
SELECT COUNT(*) FROM order_items;
-- 9: nothing was lost
```

Until `COMMIT`, other sessions don't see your changes, and `ROLLBACK` undoes them. How the database keeps transactions isolated from each other is covered in System Design.

Some tools add safeguards: MySQL's `--safe-updates` option restricts UPDATE and DELETE unless they use a key condition or a LIMIT; large queries can be restricted further. Many GUI clients warn about unfiltered writes. In PostgreSQL's `psql`, autocommit is on by default, so each statement commits immediately unless you type `BEGIN` first.

## Key takeaways
- A DELETE removes rows; an UPDATE can clear an individual nullable value.
- Omitting WHERE changes or removes every qualifying table row.
- Inspect the target rows and affected count within a deliberate transaction.

## Further reading
- [Data manipulation — PostgreSQL documentation](https://www.postgresql.org/docs/current/dml.html)
