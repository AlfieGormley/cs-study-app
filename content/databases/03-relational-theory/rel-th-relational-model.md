---
id: rel-th-relational-model
title: The relational model
level: basic
minutes: 10
summary: Relations, tuples, domains and keys as Codd defined them, the integrity rules that follow, and the places where SQL tables quietly break the theory.
---

In 1970 Edgar F. Codd, a researcher at IBM, published *A Relational Model of Data for Large Shared Data Banks*. At the time, databases were navigational: programs followed pointers from one record to the next, and if the storage layout changed, the programs broke.

Codd's idea was to describe data purely as **sets of facts**, with no pointers and no visible storage order. Programs say *what* they want, and the system works out *how* to fetch it. That separation, called **data independence**, is why you can add an index to a Postgres table today without touching a single query.

This lesson defines the vocabulary precisely. Every later lesson (algebra, dependencies, normal forms) builds on it.

## Relations, tuples and attributes

A **relation** is a set of tuples that all share the same heading. Informally it is a table, but the precise definition matters.

```
Student
+-----+------+------+
| sid | name | year |   <- heading
+-----+------+------+
|  1  | Ada  |  2   |   <- tuple
|  2  | Ben  |  1   |
|  3  | Cat  |  2   |
+-----+------+------+
```

| Theory | SQL | Meaning |
|---|---|---|
| Relation | Table | A set of tuples |
| Tuple | Row | One fact |
| Attribute | Column | A named role |
| Domain | Type | Allowed values |

- The **heading** is a set of `(attribute, domain)` pairs, such as `(year, INTEGER)`.
- A **domain** is the set of values an attribute may take. Codd required values to be **atomic** from the database's point of view (more on that in the normal forms lesson).
- The **degree** (or arity) is the number of attributes: 3 above.
- The **cardinality** is the number of tuples: 3 above. It changes as rows are inserted; the degree does not.

### Each tuple is a true statement

The most useful way to read a relation is as a **predicate** with blanks:

> Student *sid* is called *name* and is in year *year*.

Every tuple fills in the blanks to make a true proposition. The tuple `(2, Ben, 1)` asserts "Student 2 is called Ben and is in year 1."

This is the **closed-world assumption**: if a tuple is absent, the statement is taken to be false. If there is no row for student 7, the database is claiming there is no student 7. SQL NOT EXISTS always tests whether a query returns rows; interpreting absence as a fact about the world additionally assumes the stored relation is complete for its predicate.

## Consequences of "a set of tuples"

Because a relation is a mathematical set, three properties follow directly:

1. **No duplicate tuples.** Stating the same fact twice adds nothing. A set cannot contain an element twice.
2. **No tuple order.** Sets are unordered. "The first row" has no meaning; only `ORDER BY` imposes an order on a result.
3. **No attribute order.** The heading is a set too, so attributes are identified by name, not position.

> [!warning] SQL tables are not quite relations
> SQL is a pragmatic descendant of the model, and it deviates in ways that bite:
> - Tables and query results are **bags** (multisets). Without a key, `INSERT` can add the same row twice, and `SELECT dept FROM emp` returns duplicates unless you write `DISTINCT`.
> - Columns have a position. `SELECT *` and `INSERT INTO t VALUES (...)` depend on it.
> - SQL has **NULL**, which the original model did not, giving three-valued logic.
> - Rows have a physical order on disk, but no guaranteed order in results. Postgres can return rows in a different order between two runs of the same query.

Codd later criticised SQL for these departures, and authors such as Chris Date and Hugh Darwen have argued the same for decades. In practice you get close to the model by giving every table a key and writing `DISTINCT` when you mean a set.

## Keys

A relation has no duplicate tuples, so the full set of attributes always identifies a tuple uniquely. Usually a smaller set does too.

- A **superkey** is any set of attributes whose values are unique across every tuple the relation could legally contain.
- A **candidate key** is a *minimal* superkey: remove any attribute and it stops being unique.
- The **primary key** is the candidate key you choose as the main identifier. The others are **alternate keys**, normally enforced in SQL with UNIQUE plus NOT NULL on their attributes.

Consider `Employee(emp_id, email, name, dept)`:

| Attribute set | Superkey? | Candidate key? |
|---|---|---|
| `{emp_id}` | Yes | Yes |
| `{email}` | Yes | Yes |
| `{emp_id, name}` | Yes | No, not minimal |
| `{name, dept}` | No | No |

> [!tip] Keys are about rules, not current data
> A key is a claim about *every legal state* of the relation, not the rows you happen to have. If today no two employees share a name, `{name}` is still not a key, because the business allows two people called Sam. Keys come from the domain, and you find them by asking "can this ever repeat?"

### Foreign keys

A **foreign key** is a set of attributes in one relation whose values must appear as a key in another (or the same) relation.

```
Enrolled(sid, cid)
  sid -> Student.sid
  cid -> Course.cid
```

The arrows say that every `sid` in `Enrolled` must be the `sid` of some existing student. Foreign keys are how relations refer to each other without pointers: the reference is a *value*, matched at query time by a join.

## Integrity rules

The model comes with constraints that every database state must satisfy.

1. **Entity integrity**: no attribute of a primary key may be NULL. A fact about "a student whose id is unknown" cannot be identified, so it cannot be referred to.
2. **Referential integrity**: every foreign key value either matches an existing key value in the referenced relation or (if allowed) is NULL.
3. **Domain constraints**: values come from the attribute's domain (`year` is an integer from 1 to 4, say).
4. **Key constraints**: no two tuples agree on a candidate key.

In PostgreSQL these map to DDL (create the referenced course table first). SQLite ordinary rowid tables have a historical exception allowing NULL in some declared primary keys; use explicit NOT NULL, STRICT or WITHOUT ROWID as appropriate:

```sql
CREATE TABLE student (
  sid   INT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name  TEXT NOT NULL,
  year  INT CHECK (year BETWEEN 1 AND 4)
);

CREATE TABLE enrolled (
  sid INT REFERENCES student(sid),
  cid TEXT REFERENCES course(cid),
  PRIMARY KEY (sid, cid)
);
```

The composite primary key on `enrolled` does two jobs. It identifies each enrolment, and it stops the same student enrolling on the same course twice.

When a referenced row is deleted, the foreign key's `ON DELETE` action decides what happens: `NO ACTION`/`RESTRICT` (the default family: reject the delete), `CASCADE` (delete the referencing rows), `SET NULL` or `SET DEFAULT`.

## Why the model won

The navigational databases of the 1960s, such as IBM's IMS (hierarchical) and CODASYL (network) systems, were fast for the access paths they were built for, and painful for everything else. The relational model offered three things they could not.

- **Physical data independence.** Indexes, partitioning and storage format can change without changing queries.
- **Logical data independence.** Views let you restructure tables while keeping old queries working.
- **Declarative queries.** Because queries are expressed over sets with well-defined operators (the next lesson), an optimiser can rewrite them into equivalent, cheaper forms.

The doubt in the 1970s was whether a declarative system could ever be fast enough. IBM's System R and Berkeley's Ingres answered that by the late 1970s; System R also produced SQL and the first cost-based optimiser. Oracle, DB2, Postgres (a descendant of Ingres research) and SQLite all follow.

> [!note] NULL, briefly
> Codd added NULL in later work to represent missing information, and SQL adopted it. Comparisons with NULL yield *unknown*, so `WHERE x = NULL` matches nothing, and `NOT IN` against a list that contains a NULL returns no rows. The SQL fundamentals module covers the details. For theory, the key point is that NULL breaks the clean "each tuple is a true proposition" reading, which is one reason designers try to minimise nullable columns.

## Common pitfalls

- **Tables without keys.** A log table with no primary key accumulates exact duplicates after a retried insert, and a predicate using only those stored attribute values cannot distinguish the copies; removing one may require a physical row identifier or a dialect-specific technique.
- **Relying on row order.** `SELECT ... LIMIT 1` without `ORDER BY` returns *some* row. It may change after a `VACUUM`, an index change or a parallel plan.
- **Mistaking current data for a rule.** Declaring `UNIQUE (name)` because today's names are unique will reject a legitimate insert later.
- **Pointers in disguise.** Storing `"row 5 of the other table"` or array positions as references reintroduces the navigational coupling Codd removed. Refer to rows by key value.

## Key takeaways
- A relation is a **set** of tuples over a heading of named, typed attributes; each tuple is a true statement, and absent tuples are taken as false.
- Sets have no duplicates and no order. SQL tables are bags with ordered columns and NULLs, so add keys and use `DISTINCT` deliberately.
- Every candidate key is a minimal superkey; the primary key is one chosen candidate key. Distinct candidate keys need not contain one another. Keys are business rules about all legal states, not observations about current rows.
- Foreign keys link relations by **value**, and referential integrity keeps those values valid.
- Data independence and declarative queries are what let databases optimise and evolve without breaking applications.

## Further reading
- [A Relational Model of Data for Large Shared Data Banks — E. F. Codd (1970, PDF)](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf)
- [Relational model — Wikipedia](https://en.wikipedia.org/wiki/Relational_model)
- [Candidate key — Wikipedia](https://en.wikipedia.org/wiki/Candidate_key)
- [Constraints — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [Codd's 12 rules — Wikipedia](https://en.wikipedia.org/wiki/Codd%27s_12_rules)
