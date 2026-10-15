---
id: sql-alter-sqlite
title: Evolve SQLite tables within supported ALTER operations
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: Migrations apply versioned schema changes in order.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## Changing a live schema

Schemas change for as long as the application lives, through **migrations**: versioned DDL scripts applied in order by tools such as Flyway, Alembic or Rails migrations. Developers can rely on a few rules of thumb.

### What SQLite can ALTER

SQLite has long supported `RENAME TO`, `RENAME COLUMN` (3.25), `ADD COLUMN`, and `DROP COLUMN` (3.35). Version 3.53.0 (April 2026) added `ALTER COLUMN ... SET NOT NULL` and `DROP NOT NULL`, plus adding and dropping named CHECK constraints. Anything else, such as changing a type or adding a foreign key, still means the documented rebuild: create a new table, copy the rows across, drop the old table and rename the new one, all in one transaction.

For a populated table, adding an ordinary `NOT NULL` column needs a non-NULL value for existing rows, commonly supplied by a default. PostgreSQL can add it without a default to an empty table; SQLite imposes its documented default restriction:

```sql
-- Try each addition on a fresh populated
-- shop.
ALTER TABLE customers
  ADD COLUMN phone TEXT NOT NULL;
-- SQLite: Cannot add a NOT NULL
-- column with default value NULL
ALTER TABLE customers
  ADD COLUMN tier TEXT NOT NULL
  DEFAULT 'std';   -- fine
```

For these two alternatives, use separate copies of the original populated customers table. The failed phone addition leaves its schema unchanged. The tier addition succeeds and gives each of its five existing rows the value `std`; later inserts that omit tier receive the same default. A default is used for omission, so it does not turn an explicitly supplied NULL into `std`.

Before a rebuild, inspect the original schema's constraints, indexes, triggers and dependent views. Copying just its column names can silently drop protection or break dependencies. Follow SQLite's documented rebuild sequence, preserve the objects that still apply, and run `PRAGMA foreign_key_check` before committing. If a step fails, explicitly roll back instead of committing the earlier successful steps. Rehearse the migration on a copy and verify both the resulting schema and row counts.

## Key takeaways
- Migrations apply versioned schema changes in order.
- SQLite ALTER support depends on the engine version.
- A new required column needs values for existing rows; a default can provide them.

## Further reading
- [ALTER TABLE — SQLite documentation](https://www.sqlite.org/lang_altertable.html)
