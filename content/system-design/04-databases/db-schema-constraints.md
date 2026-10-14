---
id: db-schema-constraints
title: Schemas, constraints and exact money
level: basic
minutes: 3
summary: Use typed tables and ordinary constraints to reject invalid rows, and choose exact representations for money.
sourceLesson: db-relational-acid
---

Relational databases are a common choice for transactional data: PostgreSQL, MySQL, SQL Server, Oracle, or a cloud variant such as Amazon Aurora. Before reaching for anything more exotic, you need to know what the relational model gives you for free.

## The relational model

A relational database stores data in **database tables** (relations). Each table has a fixed set of typed **database columns**, and each **database row** is one record.

- A **primary key** uniquely identifies each row (`users.id`).
- A **foreign key** is one or more columns referring to an eligible unique or primary key, possibly in the same table (`orders.user_id → users.id`). The database can enforce that the referenced row exists.
- **Constraints** (`NOT NULL`, `UNIQUE`, `CHECK`) push data rules into the database so that every application that writes to it obeys them.

```sql
-- Reject missing or duplicated emails.
CREATE TABLE users (
  id         bigserial PRIMARY KEY,
  email      text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL
             DEFAULT now()
);

-- Require a real user and nonnegative cost.
CREATE TABLE orders (
  id       bigserial PRIMARY KEY,
  user_id  bigint NOT NULL
           REFERENCES users(id),
  total_p  integer NOT NULL
           CHECK (total_p >= 0),
  status   text NOT NULL
);
```

The **schema** is the set of table definitions. Relational databases are *schema-on-write*: data that doesn't fit the schema is rejected when you write it. Document stores often permit flexible document shapes, but many also enforce declared validation rules; readers must handle permitted historical shapes.

> [!tip] Store money as integers
> `total_p` stores pence. Floating-point types can't represent 0.10 exactly, so sums drift. Use integer minor units or `numeric`.

## What ordinary constraints can express

A foreign key alone permits NULL, so add NOT NULL when every order must name a user. A CHECK can test the row being written, such as a nonnegative total; PostgreSQL does not support a CHECK that continuously validates other table rows. A rule such as "invoice total equals the sum of its lines" needs a suitable redesign or another enforcement mechanism.

## Key takeaways
- A primary key identifies a row; foreign keys and NOT NULL work together to require a valid reference.
- UNIQUE and CHECK enforce declared rules, with limits on what a row constraint can express.
- Store currency in integer minor units or exact numeric values.

## Further reading
- [PostgreSQL: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
