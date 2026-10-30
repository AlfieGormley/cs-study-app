---
id: asql-recursive-hierarchies
title: Walking a staff hierarchy
level: intermediate
minutes: 3
summary: Choose the anchor and join direction to walk down or up a hierarchy.
sourceLesson: asql-ctes
---

A recursive CTE starts with anchor rows and repeatedly joins the newest rows to find more. Here staff has Mia 1, Raj 2, Sam 3, Tom 4, Uma 5 and Vic 6, with managers shown in the tree.

### Walking a hierarchy

```sql
-- Follow the manager/report relation.
CREATE TABLE staff (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  manager_id INTEGER
    REFERENCES staff(id)
);
```

```
Mia (1)
├── Raj (2)
│   ├── Tom (4)
│   │   └── Vic (6)
│   └── Uma (5)
└── Sam (3)
```

Populate staff from the tree: Mia’s manager is NULL; Raj and Sam report to Mia; Tom and Uma to Raj; Vic to Tom. The whole org chart, with depth and path:

```sql
-- Follow the manager/report relation.
WITH RECURSIVE chain AS (
  SELECT id, name, 0 AS depth,
         name AS path
  FROM staff
  WHERE manager_id IS NULL
  UNION ALL
  SELECT s.id, s.name, c.depth + 1,
         c.path || ' > ' || s.name
  FROM staff s
  JOIN chain c
    ON s.manager_id = c.id
)
SELECT depth, path FROM chain
ORDER BY path;
```

| depth | path |
|---|---|
| 0 | Mia |
| 1 | Mia > Raj |
| 2 | Mia > Raj > Tom |
| 3 | Mia > Raj > Tom > Vic |
| 2 | Mia > Raj > Uma |
| 1 | Mia > Sam |

The `depth` column starts at 0 in the anchor row, and each recursive pass adds 1 to the depth inherited from the manager's row, so depth counts the joins from the root: Vic, three levels below Mia, gets 3.

The anchor is Mia. Pass 1 joins staff to {Mia} and finds Raj and Sam. Pass 2 finds Tom and Uma (Sam has no reports). Pass 3 finds Vic. Pass 4 finds nothing, so the loop ends.

Reverse the join to walk **up**: start from Vic and join `s.id = up.manager_id`. That gives Vic, Tom, Raj, Mia, the chain of command.

> [!warning] Postgres is strict about types
> If the `staff.name` column were `varchar(10)`, Postgres rejects the query above: `recursive query "chain" column 4 has type character varying(10) in non-recursive term but type character varying overall`. The concatenation operator returns text, and resolving the UNION removes the varchar length constraint; that result does not match the anchor's varchar(10). Cast the anchor: `name::text AS path`. SQLite has no such check.

## Key takeaways
- Choose the anchor and join direction to walk down or up a hierarchy.
- PostgreSQL checks recursive output types; cast a growing varchar path to text.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
