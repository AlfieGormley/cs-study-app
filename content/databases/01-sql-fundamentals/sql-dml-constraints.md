---
id: sql-dml-constraints
title: INSERT, UPDATE, DELETE and constraints
level: intermediate
minutes: 14
summary: Changing data safely. Writing inserts, updates and deletes, wrapping risky changes in a transaction, and letting NOT NULL, UNIQUE, CHECK and foreign keys reject bad data for you.
---

Reading data can only give you a wrong answer. Writing data can destroy it. This lesson covers the three statements that change rows, known together as **DML** (data manipulation language): `INSERT`, `UPDATE` and `DELETE`. It also covers the **constraints** that make the database refuse changes that would break your rules.

The examples use the module's shop schema. Each one starts from the original data.

## INSERT

Always name the columns you are filling:

```sql
INSERT INTO customers (name, city)
VALUES ('Femi', 'Leeds');
```

Columns you leave out get their **default**, which is NULL unless the table says otherwise. Here `referred_by` is NULL. `id` is an `INTEGER PRIMARY KEY`, so SQLite assigns the next number, 6. (PostgreSQL uses an identity column or sequence for the same job; see the next lesson.)

`INSERT INTO customers VALUES (...)` without a column list also works, but it depends on the column order in the table. Add a column later and every such statement breaks, or worse, puts values in the wrong columns.

### Several rows, and RETURNING

One statement can insert many rows, which is much faster than many single-row statements because each statement has its own round trip and commit overhead:

```sql
INSERT INTO products (name, price)
VALUES ('Jug', 12), ('Tray', 15)
RETURNING id, name;
```

| id | name |
|---|---|
| 6 | Jug |
| 7 | Tray |

`RETURNING` hands back the rows as they were written, including generated ids and defaults, without a second query. PostgreSQL has had it for a long time; SQLite added it in 3.35.

### INSERT ... SELECT

The rows can come from a query instead of `VALUES`:

```sql
INSERT INTO products
  (name, price, category)
SELECT name || ' XL', price * 2,
       category
FROM products
WHERE category = 'home';
```

This adds "Lamp XL" at £80 and "Rug XL" at £180. The copy happens inside the database, so no data travels to your application and back.

If a row might already exist, `INSERT ... ON CONFLICT` (an **upsert**) can update it instead. Module 2 covers upserts properly.

## UPDATE

`UPDATE` changes columns in every row that matches `WHERE`:

```sql
UPDATE products
SET price = price + 5
WHERE category = 'kitchen'
RETURNING name, price;
```

| name | price |
|---|---|
| Kettle | 35 |
| Toaster | 30 |

The right-hand side of `SET` sees the **old** row values. `SET a = b, b = a` swaps two columns in standard SQL and in PostgreSQL and SQLite, because both expressions read the values from before the update.

`WHERE` can use a subquery:

```sql
UPDATE products SET price = price * 2
WHERE price > (SELECT AVG(price)
               FROM products);
```

The average (38.6) is computed from the table as it was before the statement, so Lamp and Rug are doubled and the moving average doesn't change who qualifies.

To update using another table, PostgreSQL and SQLite (3.33+) both support `UPDATE ... FROM`. Mark every London customer's orders:

```sql
UPDATE orders SET status = 'vip'
FROM customers c
WHERE c.id = orders.customer_id
  AND c.city = 'London';
```

That updates 101, 102 and 105. MySQL spells this differently (`UPDATE orders JOIN customers ...`), so this is one place where portable SQL is hard.

## DELETE

```sql
DELETE FROM order_items
WHERE order_id = 105;
```

`DELETE` removes whole rows. To remove a value, `UPDATE` it to NULL instead. To empty a table quickly, `TRUNCATE` (PostgreSQL) skips per-row work, but it is all-or-nothing and doesn't fire row-level triggers. SQLite has no `TRUNCATE`; it optimises an unfiltered `DELETE FROM t` instead.

## The missing WHERE

`UPDATE products SET category = 'sale';` changes **every** product. `DELETE FROM order_items;` removes all nine order lines. Both are valid statements, and both run instantly.

> [!warning] A safe routine for risky changes
> 1. Write the `WHERE` clause first, as a `SELECT`, and check the rows and count.
> 2. Start a transaction with `BEGIN`.
> 3. Run the `UPDATE` or `DELETE` with the same `WHERE`. Check the affected row count it reports.
> 4. `COMMIT` if it matches, `ROLLBACK` if it doesn't.

```sql
BEGIN;
DELETE FROM order_items;
-- 9 rows: that's all of them!
ROLLBACK;
SELECT COUNT(*) FROM order_items;
-- 9: nothing was lost
```

Until `COMMIT`, other sessions don't see your changes, and `ROLLBACK` undoes them. How the database keeps transactions isolated from each other is covered in System Design.

Some tools add guard rails: MySQL's `--safe-updates` option refuses an `UPDATE` or `DELETE` without a key in `WHERE`, and many GUI clients warn about it. In PostgreSQL's `psql`, autocommit is on by default, so each statement commits immediately unless you type `BEGIN` first.

## Constraints

A constraint is a rule the database checks on every write. If a change would break it, the statement fails with an error and its changes are undone. Constraints are your last line of defence: application code has bugs, and data is often written by more than one program.

| constraint | rejects |
|---|---|
| `NOT NULL` | a missing value |
| `UNIQUE` | a duplicate |
| `PRIMARY KEY` | NULL or duplicate id |
| `FOREIGN KEY` | a reference to nothing |
| `CHECK (...)` | a rule returning FALSE |

The errors from SQLite on the shop schema:

```sql
INSERT INTO customers (name)
VALUES (NULL);
-- NOT NULL constraint failed:
--   customers.name

INSERT INTO customers
VALUES (1, 'Zed', 'York', NULL);
-- UNIQUE constraint failed:
--   customers.id

INSERT INTO orders
  (customer_id, ordered_on, status)
VALUES (99, '2026-04-01', 'pending');
-- FOREIGN KEY constraint failed
```

PostgreSQL's messages name the constraint, for example `duplicate key value violates unique constraint "customers_pkey"` and `insert or update on table "orders" violates foreign key constraint "orders_customer_id_fkey"`. Naming constraints yourself (`CONSTRAINT price_positive CHECK (price > 0)`) makes those messages easier to act on.

`DEFAULT` isn't a constraint, but it sits alongside them: `created TEXT NOT NULL DEFAULT CURRENT_DATE` fills in today's date when the insert omits the column. `INSERT INTO t DEFAULT VALUES` inserts a row made entirely of defaults.

### CHECK

```sql
stars INTEGER NOT NULL
  CHECK (stars BETWEEN 1 AND 5)
```

Inserting 6 fails with `CHECK constraint failed: stars BETWEEN 1 AND 5`. Remember from the NULL lesson that a CHECK passes when its result is UNKNOWN, so pair it with `NOT NULL` if the value is required. A CHECK can only see the row being written. Rules across rows or tables need a UNIQUE constraint, a foreign key, a trigger or application logic.

### Foreign keys

`orders.customer_id REFERENCES customers(id)` says every order's customer must exist (or be NULL, like the guest order). The database checks both directions:

- Inserting an order for customer 99 fails: there is no such customer.
- Deleting customer 1 fails while orders 101 and 102 still point at her.

What happens on delete is your choice:

| `ON DELETE` | deleting the parent |
|---|---|
| `NO ACTION` (default) | fails if children exist |
| `RESTRICT` | fails, checked at once |
| `CASCADE` | deletes the children |
| `SET NULL` | sets children's FK to NULL |

`NO ACTION` and `RESTRICT` differ only in timing: `NO ACTION` can be deferred to the end of the transaction, `RESTRICT` cannot. `CASCADE` suits rows that have no meaning without their parent, such as reviews of a product or the items of an order. Be wary of using it widely: one `DELETE` of a customer could silently remove years of order history. For records you must keep, `RESTRICT` plus a soft-delete flag is safer. `SET NULL` fits optional links, such as `referred_by`: if the referrer is deleted, the customer remains, unreferred.

> [!warning] SQLite doesn't enforce foreign keys by default
> For backwards compatibility, SQLite ignores `REFERENCES` unless each connection runs `PRAGMA foreign_keys = ON;`. With it off, the order for customer 99 is accepted, and deleting Asha leaves orders 101 and 102 pointing at nobody. PostgreSQL always enforces foreign keys. If you use SQLite, turn the pragma on wherever you open a connection.

### Deferred constraints

Sometimes rows that refer to each other must be inserted in an awkward order. A constraint declared `DEFERRABLE INITIALLY DEFERRED` is checked at `COMMIT` instead of after each statement. Both PostgreSQL and SQLite support this for foreign keys, and PostgreSQL also for UNIQUE. If the reference is still broken at commit time, the commit fails.

## Statements are atomic

With the default constraint-error handling used here, a failed statement rolls back its row changes. SQLite has other conflict policies: `FAIL` can retain earlier row changes from the same statement, and `IGNORE` can skip offending rows. PostgreSQL sequence increments and external side effects are also not undone by transaction rollback:

```sql
INSERT INTO products (name, price)
VALUES ('Jug', 12), ('Tray', NULL);
-- NOT NULL constraint failed
```

Jug was valid, but it is not inserted either. The products table still has five rows.

Inside a transaction, the two databases differ after an error:

- **SQLite**, for the default `ABORT` constraint policy used here, undoes the failed statement. Earlier statements in the transaction remain pending, and `COMMIT` keeps them. Other conflict policies and errors can have different effects.
- **PostgreSQL** marks the whole transaction as failed. Every further statement errors with `current transaction is aborted, commands ignored until end of transaction block`, and `COMMIT` acts as a `ROLLBACK`. Use a `SAVEPOINT` if you want to recover from an error and carry on.

Application code that catches a constraint error and carries on within the same transaction works in SQLite but not in PostgreSQL.

## Key takeaways
- Always name columns in `INSERT`. Use multi-row inserts and `RETURNING` to cut round trips.
- `SET` expressions see the old row; `UPDATE ... FROM` updates using another table.
- Run the `WHERE` as a `SELECT` first, and do risky changes inside `BEGIN` ... `COMMIT`/`ROLLBACK`.
- Constraints (NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY, CHECK) are checked on every write; failures undo the whole statement.
- Choose `ON DELETE` behaviour deliberately: `CASCADE` for dependent rows, `RESTRICT` for history, `SET NULL` for optional links.
- SQLite enforces foreign keys only with `PRAGMA foreign_keys = ON`. PostgreSQL aborts the whole transaction after an error.

## Further reading
- [Data manipulation — PostgreSQL documentation](https://www.postgresql.org/docs/current/dml.html)
- [Constraints — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [SQLite foreign key support](https://www.sqlite.org/foreignkeys.html)
- [The UPDATE statement — SQLite documentation](https://www.sqlite.org/lang_update.html)
- [The RETURNING clause — SQLite documentation](https://www.sqlite.org/lang_returning.html)
