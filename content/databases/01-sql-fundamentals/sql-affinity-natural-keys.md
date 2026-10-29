---
id: sql-affinity-natural-keys
title: Enforce types and separate identity from business keys
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: Ordinary SQLite type affinity can store text in an INTEGER column.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## SQLite's type affinity versus strict typing

PostgreSQL rejects a value of the wrong type. SQLite, by default, treats the declared type as a preference, called **type affinity**:

```sql
-- Affinity converts values when possible.
CREATE TABLE loose
  (n INTEGER, d TEXT);
INSERT INTO loose VALUES
  ('abc', 12), ('42', 3.5);
```

| n | typeof(n) | d | typeof(d) |
|---|---|---|---|
| abc | text | 12 | text |
| 42 | integer | 3.5 | text |

`'42'` was converted to an integer because it looked like one. `'abc'` couldn't be converted, so SQLite stored text in an INTEGER column without complaint. Since 3.37, a `STRICT` table rejects incompatible stored values, although its supported type names and conversion rules still differ from PostgreSQL:

```sql
-- STRICT refuses the incompatible value.
CREATE TABLE tight
  (n INTEGER, d TEXT) STRICT;
INSERT INTO tight VALUES ('abc', 'x');
-- cannot store TEXT value in
-- INTEGER column tight.n
```

`'42'` is still converted to 42, which is a lossless change. Use `STRICT` for new SQLite tables.

## Keys

A **natural key** is a real-world identifier: an email address, an ISBN, a vehicle registration. A **surrogate primary key** is a meaningless generated number or UUID.

Natural keys look attractive, but real-world identifiers change (people change email; registrations are transferred) and are rarely as unique as promised. A primary key is copied into every referencing table, so changing it means updating them all.

> [!analogy] Real-world analogy: a membership number versus a phone number
> A gym could file members under their phone numbers, but people change numbers, and every booking and payment record would then need correcting. Instead it gives each member a membership number that never changes, and keeps the phone number as contact detail.
>
> **How it maps:** The membership number is the surrogate primary key, copied into every referencing table. The phone number is the natural key: still a real rule ("no two members share a number" is a `UNIQUE` constraint), but free to change in one place.
>
> **Where it stops:** A generated number is only stable if nothing updates it; the database does not make it immutable by itself. And a surrogate primary key does not stop the same person registering twice with different details; only the natural-key constraints and good data checks do that.

The common pattern is:

- a surrogate primary key for identity and foreign keys, and
- a `UNIQUE` constraint on the natural key to enforce the business rule.

```sql
-- Column definition inside CREATE TABLE.
email TEXT NOT NULL UNIQUE
```

Watch case: `'Asha@x.com'` and `'asha@x.com'` are different strings, so both pass a plain UNIQUE. A unique index on `lower(email)` catches it (PostgreSQL also offers the `citext` extension).

## Key takeaways
- Ordinary SQLite type affinity can store text in an INTEGER column.
- STRICT tables require compatible values, including lossless conversions.
- Keep mutable business identifiers UNIQUE beside a stable surrogate primary key.

## Further reading
- [Datatypes in SQLite (type affinity)](https://www.sqlite.org/datatype3.html)
- [STRICT tables — SQLite documentation](https://www.sqlite.org/stricttables.html)
