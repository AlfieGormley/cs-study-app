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


Each pass sees only the rows produced by the *previous* pass, not the whole result so far. The loop stops when a pass produces no rows. In set notation:

```formula
W_0 = A
W_{k+1} = R(W_k)
T = W_0 + W_1 + … + W_m
W_{m+1} = ∅
where
W_0: the anchor's rows, the first working table
A: the rows the anchor (non-recursive term) returns
W_k: the working table after pass k: only the rows that pass produced
W_{k+1}, W_{m+1}: the rows the next pass produces; W_{m+1}, the pass after the last productive one, is empty
W_1, W_m: the working tables after pass 1 and after the last pass that produced rows
R: the recursive term, run with the CTE's name standing for W_k
k: the pass number, 0 for the anchor, then later passes
m: the number of the last pass that produced any rows
T: everything the CTE returns
+: here, append one batch of rows after another, keeping duplicates (UNION ALL)
…: and every batch in between
∅: the empty set: no rows
In words: start with the anchor's rows, repeatedly feed only the newest rows into the recursive term, append whatever it produces, and stop at the first pass that produces nothing.
```

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

Pass 1 sees {1} and makes {2}; pass 2 sees {2} and makes {3}; and so on until the pass that sees {5} makes nothing, because `5 < 5` is false. **The `WHERE` is the termination condition.** Without it there is no logical stop condition; execution may eventually error or be cancelled. Pass by pass:

```formula
i_0 = 1
i_{k+1} = i_k + 1   if i_k < 5
i_4 = 5
where
i_0: the anchor's value, 1
i_k: the value in the working table after pass k
i_{k+1}: the value the next pass makes from it
i_4: the value after pass 4
k: the pass number, starting at 0 for the anchor
<: strictly less than
In words: each pass adds 1 to the previous pass's value, but only while that value is below 5. Pass 5 reads 5, and 5 < 5 is false, so it makes nothing and the loop stops; so the CTE returns the five rows 1 to 5.
```

SQLite accepts recursive self-reference without the RECURSIVE modifier, but PostgreSQL requires it. Write it explicitly for both engines. A NULL-valued row is still a row: termination depends on an empty working table, not on a particular value. PostgreSQL has no built-in default recursion-depth cap; use a terminating predicate and a suitable statement timeout when testing.

## Key takeaways
- Each recursive pass reads the preceding working table.
- UNION removes repeated complete rows; UNION ALL keeps them.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
