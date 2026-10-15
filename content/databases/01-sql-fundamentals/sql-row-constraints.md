---
id: sql-row-constraints
title: Enforce required values, uniqueness and row rules
level: intermediate
minutes: 3
sourceLesson: sql-dml-constraints
summary: NOT NULL requires a known value.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. Examples of writes start from that original data unless a block explicitly groups statements together.

## Constraints

A constraint is a rule enforced when relevant data changes. With the default immediate constraint handling used here, a violation fails the statement and undoes its row changes. Deferred constraints are checked later, and SQLite has alternative conflict policies, covered next. Constraints are your last line of defence: application code has bugs, and data is often written by more than one program.

| constraint | rejects |
|---|---|
| `NOT NULL` | a missing value |
| `UNIQUE` | a duplicate |
| `PRIMARY KEY` | duplicate key; normally NULL |
| `FOREIGN KEY` | a reference to nothing |
| `CHECK (...)` | a rule returning FALSE |

The shop uses SQLite's special `INTEGER PRIMARY KEY`, which generates an id for an omitted or NULL key. Ordinary non-STRICT rowid tables also have a historical quirk: other primary-key declarations can allow NULL unless explicitly NOT NULL. PostgreSQL primary keys, SQLite STRICT tables and WITHOUT ROWID tables require non-NULL keys.

The errors from SQLite on the shop schema:

```sql
-- Each insert independently violates a
-- rule.
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
-- Column definition inside CREATE TABLE.
stars INTEGER NOT NULL
  CHECK (stars BETWEEN 1 AND 5)
```

Inserting 6 fails with `CHECK constraint failed: stars BETWEEN 1 AND 5`. Remember from the NULL lesson that a CHECK passes when its result is UNKNOWN, so pair it with `NOT NULL` if the value is required. A CHECK can only see the row being written. Rules across rows or tables need a UNIQUE constraint, a foreign key, a trigger or application logic.

## Key takeaways
- NOT NULL requires a known value.
- CHECK rejects FALSE but permits UNKNOWN.
- Use UNIQUE for cross-row uniqueness, rather than a row CHECK.

## Further reading
- [Constraints — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [SQLite foreign key support](https://www.sqlite.org/foreignkeys.html)
