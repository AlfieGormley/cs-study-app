---
id: rel-th-data-independence
title: Data independence and query interfaces
level: basic
minutes: 2
sourceLesson: rel-th-relational-model
summary: Why value-based, declarative access let storage and tables change without rewriting applications.
---

## Why the model won

The navigational databases of the 1960s, such as IBM's IMS (hierarchical) and CODASYL (network) systems, were fast for the access paths they were built for, and painful for everything else. The relational model made three goals central to its interface.

- **Physical data independence.** Indexes, partitioning and storage format can change without changing queries.
- **Logical data independence.** Views let you restructure tables while keeping old queries working.
- **Declarative queries.** Because queries are expressed over sets with well-defined operators (the next lesson), an optimiser can rewrite them into equivalent, cheaper forms.

> [!analogy] Real-world analogy: an address instead of directions
> You can tell a cabbie "take me to 10 Station Road" or give turn-by-turn directions from your house. The directions break as soon as a road closes; the address keeps working, because the cabbie chooses the route on the day.
>
> **How it maps:** Turn-by-turn directions are a navigational program following stored pointers. The address is a declarative query that names the data by value, and the cabbie is the optimiser choosing an access path. A new bypass is like a new index: the address-based trip benefits without being rewritten.
>
> **Where it stops:** A cabbie might pick a different destination by mistake. An optimiser may only choose among plans that are guaranteed to return the same result, and it can only use the access paths that actually exist.

The doubt in the 1970s was whether a declarative system could ever be fast enough. IBM's System R and Berkeley's Ingres answered that by the late 1970s; System R also produced SQL and a pioneering cost-based optimiser. Oracle, DB2, Postgres (a descendant of Ingres research) and SQLite all follow.

> [!note] NULL, briefly
> SQL uses NULL to represent missing information. Comparisons with NULL yield *unknown*, so `WHERE x = NULL` matches nothing, and `NOT IN` against a list that contains a NULL returns no rows. The SQL fundamentals module covers the details. For theory, the key point is that NULL breaks the clean "each relational tuple is a true proposition" reading, which is one reason designers try to minimise nullable columns.

## Key takeaways

- Physical data independence isolates applications from storage choices.
- Logical data independence can preserve a query interface through views while tables change.

## Further reading

- [Codd: A Relational Model of Data (1970)](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
