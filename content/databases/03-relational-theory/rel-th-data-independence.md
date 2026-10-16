---
id: rel-th-data-independence
title: Data independence and query interfaces
level: basic
minutes: 2
sourceLesson: rel-th-relational-model
summary: Data independence and query interfaces, with explicit examples and the conditions that make the reasoning valid.
---

## Why the model won

The navigational databases of the 1960s, such as IBM's IMS (hierarchical) and CODASYL (network) systems, were fast for the access paths they were built for, and painful for everything else. The relational model made three goals central to its interface.

- **Physical data independence.** Indexes, partitioning and storage format can change without changing queries.
- **Logical data independence.** Views let you restructure tables while keeping old queries working.
- **Declarative queries.** Because queries are expressed over sets with well-defined operators (the next lesson), an optimiser can rewrite them into equivalent, cheaper forms.

The doubt in the 1970s was whether a declarative system could ever be fast enough. IBM's System R and Berkeley's Ingres answered that by the late 1970s; System R also produced SQL and a pioneering cost-based optimiser. Oracle, DB2, Postgres (a descendant of Ingres research) and SQLite all follow.

> [!note] NULL, briefly
> SQL uses NULL to represent missing information. Comparisons with NULL yield *unknown*, so `WHERE x = NULL` matches nothing, and `NOT IN` against a list that contains a NULL returns no rows. The SQL fundamentals module covers the details. For theory, the key point is that NULL breaks the clean "each relational tuple is a true proposition" reading, which is one reason designers try to minimise nullable columns.

## Key takeaways

- Physical data independence isolates applications from storage choices.
- Logical data independence can preserve a query interface through views while tables change.

## Further reading

- [Codd: A Relational Model of Data (1970)](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
