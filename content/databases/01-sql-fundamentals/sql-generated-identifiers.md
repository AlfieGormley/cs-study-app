---
id: sql-generated-identifiers
title: Generate ids without collisions or unwanted reuse
level: advanced
minutes: 4
sourceLesson: sql-schema-ddl
summary: Identity sequences do not advance when an explicit id bypasses generation.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

### Generating ids

| database | declaration |
|---|---|
| PostgreSQL 10+ | `GENERATED ALWAYS AS IDENTITY` |
| PostgreSQL (older) | `serial` / `bigserial` |
| SQLite | `INTEGER PRIMARY KEY` |

In PostgreSQL, prefer identity columns to `serial`. They are standard SQL, and `ALWAYS` rejects hand-written ids unless the insert says `OVERRIDING SYSTEM VALUE`. That matters because inserting explicit ids into a `serial` or `BY DEFAULT` column doesn't advance the sequence, and a later generated id collides with `duplicate key value violates unique constraint`. Use `bigint` for ids of any table that might grow large. A signed integer column spends one bit on the sign, so a 32-bit `integer` tops out at about 2.1 billion, while a 64-bit `bigint` reaches about 9.2 billion billion.

```formula reference
N_max = 2^{b − 1} − 1
N_32 = 2^31 − 1 = 2,147,483,647
N_64 = 2^63 − 1 ≈ 9.2 × 10^18
where
N_max: the largest value a signed integer of b bits can hold
b: the number of bits in the type: 32 for PostgreSQL integer, 64 for bigint
N_32: the limit of a 32-bit integer column, about 2.1 billion
N_64: the limit of a 64-bit bigint column
≈: approximately equal to
In words: each extra bit doubles the range, and one bit is used for the sign, so a 32-bit id runs out after about 2.1 billion values while a 64-bit id effectively never does.
```

Running out of 32-bit ids has caused real outages. At 1,000 new rows a second, about 2.1 billion ids last under 25 days; the same rate would take about 290 million years to exhaust a bigint. Gaps from rolled-back inserts use up ids faster than the row count suggests.

In SQLite, an `INTEGER PRIMARY KEY` column becomes an alias for the table's internal **rowid**. New ids normally follow a simple rule: the next id is one more than the largest id currently in the table. (An empty table starts at 1.) This ordinary rule assumes the current largest rowid is below the signed 64-bit maximum; at that maximum SQLite tries unused positive ids instead. So deleting the newest row lets its id be **reused**. In a table holding ids 1 to 5, delete row 5 and the next insert gets id 5 again. (In the shop itself, enforced foreign keys refuse to delete the Mug, product 5, while order lines still reference it.) Adding `AUTOINCREMENT` prevents automatic reuse of IDs from previously committed rows, at a small cost. IDs from rolled-back transactions can still be reused, and explicit IDs require separate care. It's only needed when old ids might linger elsewhere, in logs, caches or URLs.

UUIDs make sense when ids are generated outside the database. Random UUIDv4 values can make identifiers difficult to guess, but an id is never a substitute for authorisation. They scatter inserts across a B-tree index. Time-ordered UUIDv7 improves insertion locality, while exposing approximate generation time; PostgreSQL 18 added a built-in `uuidv7()` function.

## Key takeaways
- Identity sequences do not advance when an explicit id bypasses generation.
- Choose an identifier capacity that fits growth and consumed sequence values.
- SQLite normally reuses a deleted highest rowid unless AUTOINCREMENT prevents it.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
- [SQLite autoincrement](https://www.sqlite.org/autoinc.html)
