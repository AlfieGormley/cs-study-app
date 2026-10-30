---
id: asql-recursive-steps
title: Recursive working tables and termination
level: intermediate
minutes: 4
summary: Each recursive pass reads the preceding working table.
sourceLesson: asql-ctes
---

## Recursive CTEs

A recursive CTE has two parts joined by `UNION ALL` (or `UNION`):

1. The **anchor member** (non-recursive term): the starting rows.
2. The **recursive term**: a query that references the CTE itself.

For UNION ALL, PostgreSQL conceptually runs it as a loop over a *working table* (SQLite describes a row queue; the examples have the same results):

```text
Start with the anchor rows.
Keep them as the current working table.
While the working table has rows:
  Read it in the recursive term.
  Append the newly produced rows.
  Make those rows the new working table.
```

Each pass sees only the rows produced by the *previous* pass, not the whole result so far. The loop stops at the first pass that produces no rows, and the CTE returns the anchor rows plus every batch appended along the way.

> [!analogy] Real-world analogy: a phone tree
> A club passes news on with a phone tree. The organiser calls a few members; in each round, only the people who were called in the previous round make calls. When a round has nobody left to call, the news has finished spreading.
>
> **How it maps:** The organiser's first calls are the anchor rows. Each round is one pass of the recursive term, and "the people called last round" is the working table that pass reads. The full list of everyone called is the CTE's result, and the round that calls nobody is the empty pass that ends the loop.
>
> **Where it stops:** A real caller remembers who has already heard the news. With `UNION ALL`, a recursive CTE remembers nothing: if the data loops back, it keeps calling the same people forever. Preventing that is your job (see the cycles unit).

With `UNION` instead of `UNION ALL`, each pass also discards rows already in the result before they go into the next working table.

### Counting

```sql
-- Feed only the newest rows forward.
WITH RECURSIVE n(i) AS (
  SELECT 1
  UNION ALL
  SELECT i + 1 FROM n WHERE i < 5
)
SELECT i FROM n;
-- 1, 2, 3, 4, 5
```

Pass 1 sees {1} and makes {2}; pass 2 sees {2} and makes {3}; and so on until the pass that sees {5} makes nothing, because `5 < 5` is false. So the CTE returns the five rows 1 to 5. **The `WHERE` is the termination condition**, and it tests the row being *read*, not the row being made. Without it there is no logical stop condition; execution may eventually error or be cancelled.

SQLite accepts recursive self-reference without the RECURSIVE modifier, but PostgreSQL requires it. Write it explicitly for both engines. A NULL-valued row is still a row: termination depends on an empty working table, not on a particular value. PostgreSQL has no built-in default recursion-depth cap; use a terminating predicate and a suitable statement timeout when testing.

## Key takeaways
- Each recursive pass reads the preceding working table.
- UNION removes repeated complete rows; UNION ALL keeps them.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
