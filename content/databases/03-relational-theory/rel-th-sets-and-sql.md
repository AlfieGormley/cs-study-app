---
id: rel-th-sets-and-sql
title: Sets, bags and SQL results
level: basic
minutes: 3
sourceLesson: rel-th-relational-model
summary: Why relations have no duplicates or order, where SQL tables differ, and the bugs those differences cause.
---

## Consequences of "a set of relational tuples"

Because a relation is a mathematical set, three properties follow directly:

1. **No duplicate relational tuples.** Stating the same fact twice adds nothing. A set cannot contain an element twice.
2. **No tuple order.** Sets are unordered. "The first row" has no meaning; only `ORDER BY` imposes an order on a result.
3. **No attribute order.** The heading is a set too, so attributes are identified by name, not position.

> [!warning] SQL tables are not quite relations
> SQL is a pragmatic descendant of the model, and it deviates in ways that bite:
> - Tables and query results can be **bags** (multisets). Without a key, `INSERT` can add the same row twice, and `SELECT dept FROM emp` returns duplicates unless you write `DISTINCT`.
> - Columns have a position. `SELECT *` and `INSERT INTO t VALUES (...)` depend on it.
> - SQL has **NULL**, which the original model did not, giving three-valued logic.
> - Stored PostgreSQL row versions occupy physical locations, but those locations provide no guaranteed order in results. Postgres can return rows in a different order between two runs of the same query.

Chris Date and Hugh Darwen have criticised SQL’s duplicate rows and three-valued logic as departures from the relational model. In practice you get close to the model by giving every table a key and writing `DISTINCT` when you want a set.

## Common pitfalls

- **Tables without keys.** A log table with no primary key accumulates exact duplicates after a retried insert, and a predicate using only those stored attribute values cannot distinguish the copies; removing one may require a physical row identifier or a dialect-specific technique.
- **Relying on row order.** `SELECT ... LIMIT 1` without `ORDER BY` returns *some* row. It may change after a `VACUUM`, an index change or a parallel plan.
- **Mistaking current data for a rule.** Declaring `UNIQUE (name)` because today's names are unique will reject a legitimate insert later.
- **Pointers in disguise.** Storing `"row 5 of the other table"` or array positions as references reintroduces the navigational coupling Codd removed. Refer to rows by key value.

## Key takeaways

- Relations have neither duplicates nor intrinsic order; SQL can retain duplicates.
- Use deliberate duplicate removal and an ORDER BY with a unique tie-breaker when order matters.

## Further reading

- [Codd: A Relational Model of Data (1970)](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf)
- [PostgreSQL 18: constraints](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [Darwen: SQL language design and relational departures](https://www.dcs.warwick.ac.uk/~hugh/TTM/HAVING-A-Blunderful-Time.html)
