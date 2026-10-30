---
id: rel-th-integrity-rules
title: Enforcing relational integrity
level: basic
minutes: 3
sourceLesson: rel-th-relational-model
summary: Entity, referential, domain and key integrity, and how PostgreSQL constraints enforce them, NULL cases included.
---

## Foreign keys

A **foreign key** is a set of attributes in one relation whose values must appear as a key in another (or the same) relation.

An enrolment carries student id `sid` and course code `cid`. Its student id refers by value to the key of Student, and its course code to the key of Course:

```
Student(sid, ...)    Course(cid, ...)
     ^                    ^
     |                    |
Enrolled(sid,        cid)
```

The arrows say that every `sid` in `Enrolled` must be the `sid` of some existing student, and every `cid` the `cid` of some existing course. Foreign keys are how relations refer to each other without pointers: the reference is a *value*, matched at query time by a join.

## Integrity rules

The model comes with constraints that every database state must satisfy.

1. **Entity integrity**: no attribute of a primary key may be NULL. A fact about "a student whose id is unknown" cannot be identified, so it cannot be referred to.
2. **Referential integrity**: in the null-free theory, a foreign key must match a referenced key value. SQL adds nullable references. PostgreSQL’s default `MATCH SIMPLE` waives a composite reference when any referencing column is NULL; `MATCH FULL` permits a reference with all columns NULL but rejects a mixture of NULL and non-NULL. Use `NOT NULL` on every referencing column when participation is mandatory.
3. **Relational domain constraints**: values come from the attribute's domain (`year` is an integer from 1 to 4, say).
4. **Relational key constraints**: no two relational tuples agree on a candidate key.

In PostgreSQL these map to DDL (create the referenced course table first). SQLite ordinary rowid tables have a historical exception allowing NULL in some declared primary keys; use explicit NOT NULL, STRICT or WITHOUT ROWID as appropriate:

```sql
-- Referenced keys must exist first.
CREATE TABLE course (
  cid TEXT PRIMARY KEY
);

CREATE TABLE student (
  sid   INT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name  TEXT NOT NULL,
  year  INT NOT NULL
    CHECK (year BETWEEN 1 AND 4)
);

CREATE TABLE enrolled (
  sid INT REFERENCES student(sid),
  cid TEXT REFERENCES course(cid),
  PRIMARY KEY (sid, cid)
);
```

The composite primary key on `enrolled` does two jobs. It identifies each enrolment, and it stops the same student enrolling on the same course twice.

When a referenced row is deleted, the foreign key's `ON DELETE` action decides what happens: `NO ACTION` (the PostgreSQL default, with checking deferrable if declared so), `RESTRICT` (reject immediately, without deferring), `CASCADE` (delete the referencing rows), `SET NULL` or `SET DEFAULT`.

> [!analogy] Real-world analogy: a cloakroom ticket
> A cloakroom ticket carries a peg number. It is only useful if that peg exists and holds a coat. Staff will not clear a peg while a ticket for it is still out, unless the venue's rule is to void outstanding tickets when it does.
>
> **How it maps:** The ticket is a referencing row, the peg number is the foreign-key value, and the peg is the referenced key. Refusing to clear a claimed peg is `NO ACTION` or `RESTRICT`; voiding the tickets with it is `CASCADE`.
>
> **Where it stops:** A ticket names one peg in one cloakroom. A foreign key can span several columns, can point into its own table, and SQL lets a nullable reference skip the check entirely, which no cloakroom would allow.

A PostgreSQL `UNIQUE` constraint alone allows multiple NULLs by default. Use `UNIQUE` together with `NOT NULL` for a conventional alternate key. `NULLS NOT DISTINCT` changes uniqueness treatment, but still permits a missing value and is not a replacement for `NOT NULL`. A `CHECK` accepts true or unknown, so a domain range check by itself does not forbid NULL.

## Key takeaways

- Keys, domain rules and references constrain which database states are legal.
- PostgreSQL CHECK, nullable UNIQUE and nullable foreign keys need explicit NULL decisions.

## Further reading

- [Codd: A Relational Model of Data (1970)](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
