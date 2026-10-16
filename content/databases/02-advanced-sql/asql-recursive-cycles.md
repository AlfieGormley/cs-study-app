---
id: asql-recursive-cycles
title: Cycle detection and bounded recursion
level: intermediate
minutes: 3
summary: UNION stops repeated identities only if the full projected row repeats.
sourceLesson: asql-ctes
---

Use staff ids Mia 1, Raj 2, Sam 3, Tom 4, Uma 5 and Vic 6. Mia manages Raj and Sam; Raj manages Tom and Uma; Tom manages Vic. A recursive anchor is the starting row; the recursive term finds its reports.

## Cycles

Hierarchies in real data are not always trees. Suppose someone sets Mia's manager to Vic, creating a loop. The earlier root-based anchor (`manager_id IS NULL`) would now find no rows. To demonstrate the cycle, start explicitly at Mia (`WHERE id = 1`); then the recursive term keeps finding rows: Mia, Raj, Tom, Vic, Mia, Raj...

Three defences:

1. **`UNION` instead of `UNION ALL`.** `UNION` discards rows already produced. If the rows are just `(id, name)`, the second Mia is a duplicate and the loop stops (6 rows). But add a `depth` column and every row is unique again, so `UNION` no longer saves you.
2. **Track the path** and refuse to revisit:

```sql
-- Refuse to follow visited identities.
SELECT s.id,
       c.path || s.id || ','
FROM staff s
JOIN chain c
  ON s.manager_id = c.id
WHERE c.path NOT LIKE
      '%,' || s.id || ',%'
```

   with the anchor's path starting as `',1,'`. Postgres users can keep a SQL integer array and test `s.id <> ALL(c.path)`.
3. **Postgres 14+ CYCLE clause**, which does the path tracking for you:

```sql
-- Refuse to follow visited identities.
WITH RECURSIVE chain AS (
  SELECT id, name, 0 AS depth
  FROM staff WHERE id = 1
  UNION ALL
  SELECT s.id, s.name, c.depth + 1
  FROM staff s JOIN chain c
    ON s.manager_id = c.id
)
CYCLE id SET is_cycle USING path
SELECT id, depth, is_cycle FROM chain
ORDER BY depth, id;
```

   On the looped data this returns the six staff plus one extra Mia row with `is_cycle = true`, then stops.

A depth limit (`WHERE c.depth < 20`) bounds this traversal, though it can truncate legitimate deep paths. PostgreSQL 14+ also has SEARCH DEPTH FIRST or SEARCH BREADTH FIRST clauses: these produce an ordering value, which you must use in the final ORDER BY. The SEARCH clause does not control the physical visitation order. A final LIMIT is useful during experiments but may not stop recursion when a sort or join first demands all rows.

## Key takeaways
- UNION stops repeated identities only if the full projected row repeats.
- Track visited identities or use PostgreSQL CYCLE clause to prevent infinite walks.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
