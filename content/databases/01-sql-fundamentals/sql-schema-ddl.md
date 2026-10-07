---
id: sql-schema-ddl
title: Schema design and DDL
level: advanced
minutes: 16
summary: Designing tables that stay correct for years. Modelling relationships, choosing types and keys, writing CREATE TABLE in SQLite and PostgreSQL, and changing a live schema without downtime.
---

Queries come and go, but a schema lasts for years. A badly chosen type or key turns into thousands of lines of defensive code and a data-cleaning project. This lesson is about writing **DDL** (data definition language): `CREATE`, `ALTER` and `DROP`. It also covers the decisions behind those statements.

We'll redesign the module's shop schema from its requirements, then look at how to change it once it's live. Normalisation theory gets its own module (Relational Theory). How tables and indexes are stored on disk is covered in System Design.

## From requirements to tables

The shop's requirements, stated plainly:

- A customer has a name, an optional city, and may have been referred by another customer.
- A product has a name, a price and an optional category.
- A customer places many orders. A guest can also order with no account.
- An order contains many products, each with a quantity, and a product appears in many orders.

Each noun that has its own facts becomes a table. Each relationship becomes a foreign key:

```
customers 1 ──< orders 1 ──< order_items
  ^    │                          >──┐
  └────┘ referred_by                 │
              products 1 ────────────┘
```

| relationship | how it's stored |
|---|---|
| one-to-many | FK on the "many" side |
| many-to-many | a junction table |
| self-reference | FK to the same table |
| optional link | nullable FK |

`orders.customer_id` is the one-to-many link, and it is nullable for guests. `order_items` is the **junction table** that resolves orders-to-products many-to-many. Its primary key is the pair `(order_id, product_id)`: a **composite key**. It also enforces a business rule, because adding a second Kettle to order 101 fails with `UNIQUE constraint failed`. You increase `qty` instead.

### A flaw in our schema

The module's `order_items` stores only a quantity, so an order's total is computed from `products.price` **today**. Raise the Kettle's price and every historical order containing a Kettle changes value. That's wrong for invoices, refunds and accounting.

The fix is to copy the price at the moment of sale into the line item (`unit_pence`). This looks like duplication, but it's a different fact: "what this customer paid" rather than "what the product costs now". Many apparent duplicates in a well-designed schema are really **snapshots** like this.

## Choosing types

### Money: never floating point

```sql
SELECT 0.1 + 0.2 = 0.3;  -- 0 (false)
SELECT 0.1 + 0.2;
-- 0.30000000000000004
```

Binary floating point can't represent most decimal fractions exactly, so rounding errors build up in sums. Store money either as:

- **integer minor units** (pence): `price_pence INTEGER`, where £10.99 is 1099. This is exact, fast and portable, and it's how payment processors such as Stripe represent amounts.
- **exact decimals**: PostgreSQL `numeric(10,2)`. This is exact, and `SUM` of it stays exact.

Avoid `real`, `float` and `double precision` for money. Also avoid PostgreSQL's `money` type, whose formatting depends on a server locale setting.

### Dates and times

PostgreSQL has real types. Use `date` for calendar dates and `timestamptz` (timestamp with time zone) for moments in time. `timestamptz` stores an absolute instant, internally in UTC, and converts to the session's time zone on display. Plain `timestamp` stores a wall-clock reading with no zone, which becomes ambiguous the moment two servers or users disagree on time zone or a clock change happens. PostgreSQL's own wiki says to prefer `timestamptz`.

SQLite has no date type. Store ISO-8601 text (`'2026-03-09'`, or `'2026-03-09T14:30:00Z'` in UTC). It only sorts correctly if every value uses the same zero-padded format:

```sql
-- '2026-3-9' vs '2026-03-10'
SELECT t FROM dt ORDER BY t;
-- 2026-03-10
-- 2026-3-9    (wrong!)
```

A CHECK can reject badly formatted values at write time, but beware the NULL lesson. SQLite's `date('2026-3-9')` returns NULL, so `CHECK (d = date(d))` is UNKNOWN and **passes**. Use the NULL-safe form:

```sql
d TEXT NOT NULL
  CHECK (d IS date(d))
```

This rejects `'2026-3-9'`, and also `'2026-02-30'`, which `date()` turns into `'2026-03-02'`.

### Text

In PostgreSQL, `text` and `varchar(n)` are stored the same way and perform the same. `varchar(n)` just adds a length check. Use `text`, and add a `CHECK (length(name) <= 200)` where a limit is a real business rule. Avoid `char(n)`, which pads with spaces.

## SQLite's type affinity versus strict typing

PostgreSQL rejects a value of the wrong type. SQLite, by default, treats the declared type as a preference, called **type affinity**:

```sql
CREATE TABLE loose
  (n INTEGER, d TEXT);
INSERT INTO loose VALUES
  ('abc', 12), ('42', 3.5);
```

| n | typeof(n) | d | typeof(d) |
|---|---|---|---|
| abc | text | 12 | text |
| 42 | integer | 3.5 | text |

`'42'` was converted to an integer because it looked like one. `'abc'` couldn't be converted, so SQLite stored text in an INTEGER column without complaint. Since 3.37, a `STRICT` table enforces types the way PostgreSQL does:

```sql
CREATE TABLE tight
  (n INTEGER, d TEXT) STRICT;
INSERT INTO tight VALUES ('abc', 'x');
-- cannot store TEXT value in
-- INTEGER column tight.n
```

`'42'` is still converted to 42, which is a lossless change. Use `STRICT` for new SQLite tables.

## Keys

A **natural key** is a real-world identifier: an email address, an ISBN, a vehicle registration. A **surrogate key** is a meaningless generated number or UUID.

Natural keys look attractive, but real-world identifiers change (people change email; registrations are transferred) and are rarely as unique as promised. A primary key is copied into every referencing table, so changing it means updating them all. The common pattern is:

- a surrogate primary key for identity and foreign keys, and
- a `UNIQUE` constraint on the natural key to enforce the business rule.

```sql
email TEXT NOT NULL UNIQUE
```

Watch case: `'Asha@x.com'` and `'asha@x.com'` are different strings, so both pass a plain UNIQUE. A unique index on `lower(email)` catches it (PostgreSQL also offers the `citext` extension).

### Generating ids

| database | declaration |
|---|---|
| PostgreSQL 10+ | `GENERATED ALWAYS AS IDENTITY` |
| PostgreSQL (older) | `serial` / `bigserial` |
| SQLite | `INTEGER PRIMARY KEY` |

In PostgreSQL, prefer identity columns to `serial`. They are standard SQL, and `ALWAYS` rejects hand-written ids unless the insert says `OVERRIDING SYSTEM VALUE`. That matters because inserting explicit ids into a `serial` or `BY DEFAULT` column doesn't advance the sequence, and a later generated id collides with `duplicate key value violates unique constraint`. Use `bigint` for ids of any table that might grow large. Running out of 32-bit ids (about 2.1 billion) has caused real outages.

In SQLite, an `INTEGER PRIMARY KEY` column becomes an alias for the table's internal **rowid**. New ids are the current maximum plus one, so deleting the newest row lets its id be **reused**. Delete product 5 and the next insert gets id 5 again. Adding `AUTOINCREMENT` prevents automatic reuse of IDs from previously committed rows, at a small cost. IDs from rolled-back transactions can still be reused, and explicit IDs require separate care. It's only needed when old ids might linger elsewhere, in logs, caches or URLs.

UUIDs make sense when ids are generated outside the database or must not be guessable. Random UUIDv4 values scatter inserts across a B-tree index. Time-ordered UUIDv7 avoids that, and PostgreSQL 18 added a built-in `uuidv7()` function.

## The redesigned schema in PostgreSQL

```sql
CREATE TABLE customers (
  id bigint GENERATED ALWAYS
     AS IDENTITY PRIMARY KEY,
  name text NOT NULL,
  email text NOT NULL UNIQUE,
  city text,
  referred_by bigint
    REFERENCES customers (id)
    ON DELETE SET NULL,
  created_at timestamptz
    NOT NULL DEFAULT now()
);

CREATE TABLE products (
  id bigint GENERATED ALWAYS
     AS IDENTITY PRIMARY KEY,
  name text NOT NULL,
  price_pence integer NOT NULL
    CHECK (price_pence >= 0),
  category text
);

CREATE TABLE orders (
  id bigint GENERATED ALWAYS
     AS IDENTITY PRIMARY KEY,
  customer_id bigint
    REFERENCES customers (id),
  placed_at timestamptz NOT NULL
    DEFAULT now(),
  status text NOT NULL
    DEFAULT 'pending'
    CHECK (status IN ('pending',
      'shipped', 'cancelled'))
);

CREATE TABLE order_items (
  order_id bigint NOT NULL
    REFERENCES orders (id)
    ON DELETE CASCADE,
  product_id bigint NOT NULL
    REFERENCES products (id),
  qty integer NOT NULL
    CHECK (qty > 0),
  unit_pence integer NOT NULL,
  PRIMARY KEY (order_id, product_id)
);

CREATE INDEX ON orders (customer_id);
CREATE INDEX ON order_items
  (product_id);
```

Notice the decisions:

- `orders.customer_id` is nullable (guests) and uses the default `NO ACTION`, so a customer with orders can't be deleted by accident.
- `order_items` cascades: lines don't exist without their order.
- `unit_pence` snapshots the price.
- The `status` list is a CHECK. The alternatives are a PostgreSQL `ENUM` type (compact; values can be renamed with `ALTER TYPE`, but removing one requires a more involved migration) or a `statuses` lookup table with a foreign key (best when statuses carry their own data, or business users add them).

Use lower-case `snake_case` names. PostgreSQL folds unquoted identifiers to lower case, so a table created as `"OrderItems"` must be double-quoted in every query forever.

### Index your foreign keys

Neither PostgreSQL nor SQLite creates an index on a **referencing** column automatically. (Both index primary keys and UNIQUE columns.) Without the two `CREATE INDEX` lines above, "orders for customer 1" is a full table scan. In SQLite, `EXPLAIN QUERY PLAN` shows `SCAN orders` before the index exists and `SEARCH orders USING INDEX` after. A missing FK index also makes every delete of a parent row scan the child table to check for references. `order_items` needs no separate index on `order_id`, because it's the first column of the primary key.

## Changing a live schema

Schemas change for as long as the application lives, through **migrations**: versioned DDL scripts applied in order by tools such as Flyway, Alembic or Rails migrations. Developers can rely on a few rules of thumb.

### What SQLite can ALTER

SQLite has long supported `RENAME TO`, `RENAME COLUMN` (3.25), `ADD COLUMN` and `DROP COLUMN` (3.35). Version 3.53 (2026) added `ALTER COLUMN ... SET NOT NULL` and `DROP NOT NULL`, plus adding and dropping named CHECK constraints. Anything else, such as changing a type or adding a foreign key, still means the documented rebuild: create a new table, copy the rows across, drop the old table and rename the new one, all in one transaction.

For a populated table, adding an ordinary `NOT NULL` column needs a non-NULL value for existing rows, commonly supplied by a default. PostgreSQL can add it without a default to an empty table; SQLite imposes its documented default restriction:

```sql
ALTER TABLE customers
  ADD COLUMN phone TEXT NOT NULL;
-- SQLite: Cannot add a NOT NULL
-- column with default value NULL
ALTER TABLE customers
  ADD COLUMN tier TEXT NOT NULL
  DEFAULT 'std';   -- fine
```

### PostgreSQL: watch the locks

Most `ALTER TABLE` forms take an `ACCESS EXCLUSIVE` lock, which blocks reads and writes on that table. Whether that matters depends on how long the lock is held:

- **Fast, metadata only:** adding a nullable column, or (since PostgreSQL 11) adding a column with a non-volatile default such as `'std'` or `now()`. This avoids work proportional to the number of rows, but lock waits and catalogue work still determine the elapsed time.
- **Slow, rewrites or scans:** changing a column's type, adding a column with a volatile default such as `clock_timestamp()`, or `SET NOT NULL`, which scans every row to check.

Even a fast `ALTER` can cause an outage. If a long-running query holds a lock on the table, the `ALTER` waits for it, and every new query queues behind the `ALTER`. Set `lock_timeout` (for example `SET lock_timeout = '2s'`) so the migration fails fast and can be retried.

For slow changes, split the work so that the long validation phase permits ordinary reads and writes. The short catalogue changes still take locks:

```sql
-- 1. add, not yet checked
ALTER TABLE customers
  ADD CONSTRAINT email_nn
  CHECK (email IS NOT NULL)
  NOT VALID;
-- 2. check old rows, no write lock
ALTER TABLE customers
  VALIDATE CONSTRAINT email_nn;
-- 3. PG 12+ uses the valid CHECK
--    to skip the scan
ALTER TABLE customers
  ALTER COLUMN email SET NOT NULL;
```

Indexes follow the same idea. Plain `CREATE INDEX` blocks writes for the whole build. `CREATE INDEX CONCURRENTLY` doesn't, but it takes longer, can't run inside a transaction block, and leaves an `INVALID` index behind if it fails, which you must drop and retry.

Renaming or dropping a column that running code still uses breaks that code instantly. The safe pattern is **expand and contract**: add the new column, deploy code that writes both, backfill in batches, switch reads, and only then drop the old column in a later release.

## Views and DROP

A **view** is a named, stored query:

```sql
CREATE VIEW order_totals AS
SELECT oi.order_id,
  SUM(oi.qty * p.price) AS total
FROM order_items oi
JOIN products p
  ON p.id = oi.product_id
GROUP BY oi.order_id;
```

`SELECT * FROM order_totals WHERE total > 60` returns 101 (62), 102 (80) and 104 (70). A view stores no data; it runs its query each time. PostgreSQL's `MATERIALIZED VIEW` stores the result and needs `REFRESH MATERIALIZED VIEW` to update it.

`DROP TABLE IF EXISTS t` won't fail if `t` is missing, which makes scripts safe to re-run. In PostgreSQL, `DROP TABLE t CASCADE` also silently drops every view and foreign key constraint that depends on `t`. SQLite and PostgreSQL support transactional DDL for operations such as these. Explicitly roll back a failed migration: PostgreSQL normally aborts the transaction after an error, whereas SQLite can leave earlier successful statements pending and a later COMMIT could retain them. MySQL commits implicitly at each DDL statement, which is one reason migrations there need extra care.

## Key takeaways
- Turn nouns into tables and relationships into foreign keys. Many-to-many needs a junction table with a composite key.
- Snapshot facts that must not change later, such as the price paid.
- Money is integer pence or `numeric`, never float. Use `timestamptz` in PostgreSQL and zero-padded ISO-8601 text in SQLite.
- SQLite's type affinity accepts wrong types; use `STRICT` tables.
- Use surrogate keys (`bigint` identity) with `UNIQUE` on natural keys. SQLite rowids can be reused without `AUTOINCREMENT`.
- Index foreign key columns yourself.
- In PostgreSQL, know which `ALTER`s are instant and which rewrite or scan. Use `lock_timeout`, `NOT VALID` plus `VALIDATE`, `CREATE INDEX CONCURRENTLY`, and expand-and-contract.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
- [ALTER TABLE — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-altertable.html)
- [Don't do this — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Datatypes in SQLite (type affinity)](https://www.sqlite.org/datatype3.html)
- [STRICT tables — SQLite documentation](https://www.sqlite.org/stricttables.html)
- [ALTER TABLE — SQLite documentation](https://www.sqlite.org/lang_altertable.html)
- [SQLite autoincrement](https://www.sqlite.org/autoinc.html)
