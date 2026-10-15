---
id: sql-redesigned-shop
title: Read a constrained PostgreSQL shop schema
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: Constrain prices, quantities and statuses in the schema.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## The redesigned schema in PostgreSQL

```sql
-- Run this redesign in an empty database.
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

Neither PostgreSQL nor SQLite automatically adds a database index merely because a column is **referencing** a foreign key. Both provide indexed enforcement for primary and UNIQUE keys; SQLite's INTEGER PRIMARY KEY uses the rowid structure. Without an index beginning with `customer_id`, finding "orders for customer 1" can require a full table scan. In this SQLite fixture, `EXPLAIN QUERY PLAN` shows `SCAN orders` before the index and `SEARCH orders USING INDEX` after. A missing FK index can also force scans of the child table when a parent is deleted. `order_items` already has indexed access by `order_id`, the first column of its primary key. Real planners can still choose a scan when a small table makes it cheaper.

## Key takeaways
- Constrain prices, quantities and statuses in the schema.
- Snapshot unit_pence on each order line.
- Add suitable indexes on referencing foreign key columns.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
- [Don't do this — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
