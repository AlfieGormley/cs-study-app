---
id: sql-statement-error-recovery
title: Recover from failed statements and transactions
level: intermediate
minutes: 3
sourceLesson: sql-dml-constraints
summary: Default constraint handling undoes the failed statement.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. Examples of writes start from that original data unless a block explicitly groups statements together.

## Statements are atomic

With the default constraint-error handling used here, a failed statement undoes its row changes. SQLite has other conflict policies: `FAIL` can retain earlier row changes from the same statement, and `IGNORE` can skip offending rows. PostgreSQL sequence increments and external side effects are also not undone by a ROLLBACK:

```sql
-- One invalid row rejects both new
-- products.
INSERT INTO products (name, price)
VALUES ('Jug', 12), ('Tray', NULL);
-- NOT NULL constraint failed
```

Jug was valid, but it is not inserted either. The products table still has five rows.

Inside a transaction, the two databases differ after an error:

- **SQLite**, for the default `ABORT` constraint policy used here, undoes the failed statement. Earlier statements in the transaction remain pending, and `COMMIT` keeps them. Other conflict policies and errors can have different effects.
- **PostgreSQL** marks the whole transaction as failed. Every further statement errors with `current transaction is aborted, commands ignored until end of transaction block`, and `COMMIT` acts as a `ROLLBACK`. Use a `SAVEPOINT` if you want to recover from an error and carry on.

Application code that catches a constraint error and carries on within the same transaction works in SQLite but fails in PostgreSQL.

For PostgreSQL, put the part that may fail after a savepoint. If it fails, roll back to that savepoint before continuing. The rollback removes changes made since the savepoint and clears the failed state for that portion of the transaction; earlier work remains pending. A minimal example uses a duplicate primary key in the shop:

```sql
-- Recover before sending more ordinary
-- work.
BEGIN;
SAVEPOINT optional_insert;
-- Duplicate product 1: expected error.
INSERT INTO products (id, name, price)
VALUES (1, 'Duplicate', 1);
ROLLBACK TO SAVEPOINT optional_insert;
-- The transaction can now read again.
SELECT COUNT(*) FROM products;
-- 5: the rejected insert changed no rows
COMMIT;
```

In application code the error handler must actually send the rollback-to-savepoint command. Merely catching the driver exception does not repair PostgreSQL's transaction state. Do not commit earlier work by accident in SQLite either: choose whether the business operation should survive as a whole, and explicitly roll back the whole transaction if it should not.

## Key takeaways
- Default constraint handling undoes the failed statement.
- SQLite ABORT leaves earlier successful transaction statements pending.
- PostgreSQL needs rollback or rollback to a savepoint before more work.

## Further reading
- [Data manipulation — PostgreSQL documentation](https://www.postgresql.org/docs/current/dml.html)
- [Constraints — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl-constraints.html)
