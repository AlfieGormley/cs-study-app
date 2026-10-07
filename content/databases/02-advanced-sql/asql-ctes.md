---
id: asql-ctes
title: CTEs and recursive CTEs
level: intermediate
minutes: 13
summary: Naming intermediate results with WITH, how Postgres and SQLite decide whether to inline or materialise them, and recursive CTEs for hierarchies, series and graph walks.
---

A **common table expression** (CTE) is a named subquery written up front with `WITH`. An ordinary SELECT CTE provides a reusable name for a subquery and changes how a query *reads*: top to bottom, one step at a time, instead of inside out.

Recursive CTEs are different. They add something plain SQL can't otherwise express: a query that refers to its own output, which lets you walk trees and graphs of unknown depth.

This lesson uses the shop schema from the previous lesson, plus a small `staff` table.

## The basic shape

```sql
WITH spend AS (
  SELECT customer_id,
         SUM(total) AS spent
  FROM orders
  GROUP BY customer_id
)
SELECT c.name, s.spent
FROM spend s
JOIN customers c
  ON c.id = s.customer_id
WHERE s.spent > (SELECT AVG(spent)
                 FROM spend)
ORDER BY s.spent DESC;
```

| name | spent |
|---|---|
| Ana | 240 |
| Cat | 230 |

Spend per customer is Ana 240, Ben 135, Cat 230 and Dev 45, so the average is 650 / 4 = 162.5. Notice that `spend` is used twice, once in `FROM` and once in the subquery. With a derived table you would have to write the aggregation out twice.

You can chain several CTEs, each able to use the ones before it:

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', ordered_on)
           AS month,
         SUM(total) AS revenue
  FROM orders
  GROUP BY month
),
best AS (
  SELECT MAX(revenue) AS top
  FROM monthly
)
SELECT month, revenue
FROM monthly, best
WHERE revenue = top;
-- 2026-02 | 305
```

Monthly revenue is January 165, February 305 and March 180. In Postgres, write `to_char(ordered_on, 'YYYY-MM')` or `date_trunc('month', ordered_on)` instead of SQLite's `strftime`.

> [!tip] Why CTEs win code review
> Each CTE is a step you can name, read and test alone: replace the final `SELECT` with `SELECT * FROM monthly` to inspect an intermediate result. This is the main reason analytics SQL (dbt models, for example) is written as a chain of CTEs.

## Inlined or materialised?

A CTE can be executed two ways:

- **Inlined**: substituted into the outer query like a derived table, so the optimiser can push filters into it and use indexes.
- **Materialised**: computed once into a temporary result, then read from there. Good if it is expensive and used many times; bad if the outer query only needs a few rows of a huge result.

The rules differ by database and version:

| Database | Default |
|---|---|
| Postgres 11 and earlier | Always materialised |
| Postgres 12+ | Eligible non-recursive, side-effect-free SELECT CTEs: inlined if referenced once, otherwise materialised by default |
| SQLite | Planner's choice |

Both Postgres 12+ and SQLite 3.35+ accept `WITH x AS MATERIALIZED (...)` or `AS NOT MATERIALIZED (...)`. PostgreSQL ignores NOT MATERIALIZED for recursive or side-effecting CTEs, including SELECTs with volatile functions. SQLite treats these as planner hints; NOT MATERIALIZED does not forbid materialisation.

The old Postgres behaviour was famous as an **optimisation fence**. A query like this would build the CTE over every order, then filter:

```sql
WITH o AS (SELECT * FROM orders)
SELECT * FROM o WHERE id = 104;
```

Before version 12, the `id = 104` filter couldn't reach the index on `orders.id`. People deliberately used CTEs as fences to stop the planner from making a bad choice; since 12 you need `MATERIALIZED` to get that effect.

Postgres never inlines CTEs that are recursive or that have side effects (data-modifying CTEs, below).

## Recursive CTEs

A recursive CTE has two parts joined by `UNION ALL` (or `UNION`):

1. The **anchor** (non-recursive term): the starting rows.
2. The **recursive term**: a query that references the CTE itself.

For UNION ALL, PostgreSQL conceptually runs it as a loop over a *working table* (SQLite describes a row queue; the examples have the same results):

```
work := anchor rows
result := work
while work is not empty:
  new := recursive term, where the
         CTE name means "work"
  result := result + new
  work := new
```

Each pass sees only the rows produced by the *previous* pass, not the whole result so far. The loop stops when a pass produces no rows.

### Counting

```sql
WITH RECURSIVE n(i) AS (
  SELECT 1
  UNION ALL
  SELECT i + 1 FROM n WHERE i < 5
)
SELECT i FROM n;
-- 1, 2, 3, 4, 5
```

Pass 1 sees {1} and makes {2}; pass 2 sees {2} and makes {3}; and so on until the pass that sees {5} makes nothing, because `5 < 5` is false. **The `WHERE` is the termination condition.** Forget it and the query never ends.

### Walking a hierarchy

```sql
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

The whole org chart, with depth and path:

```sql
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

The anchor is Mia. Pass 1 joins staff to {Mia} and finds Raj and Sam. Pass 2 finds Tom and Uma (Sam has no reports). Pass 3 finds Vic. Pass 4 finds nothing, so the loop ends.

Reverse the join to walk **up**: start from Vic and join `s.id = up.manager_id`. That gives Vic, Tom, Raj, Mia, the chain of command.

> [!warning] Postgres is strict about types
> If the `staff.name` column were `varchar(10)`, Postgres rejects the query above: `recursive query "chain" column 4 has type character varying(10) in non-recursive term but type character varying overall`. The concatenation operator returns text, and resolving the UNION removes the varchar length constraint; that result does not match the anchor's varchar(10). Cast the anchor: `name::text AS path`. SQLite has no such check.

### Filling gaps in a series

Reports need a row for every month, even months with no sales. Generate the months, then `LEFT JOIN`:

```sql
WITH RECURSIVE months(m) AS (
  SELECT '2026-01-01'
  UNION ALL
  SELECT date(m, '+1 month')
  FROM months
  WHERE m < '2026-04-01'
)
SELECT strftime('%Y-%m', m) AS month,
       COALESCE(SUM(o.total), 0) AS rev
FROM months
LEFT JOIN orders o
  ON strftime('%Y-%m', o.ordered_on)
   = strftime('%Y-%m', m)
GROUP BY m;
```

| month | rev |
|---|---|
| 2026-01 | 165 |
| 2026-02 | 305 |
| 2026-03 | 180 |
| 2026-04 | 0 |

Postgres has a built-in for this, so you rarely need recursion there:

```sql
SELECT m::date
FROM generate_series(
  date '2026-01-01',
  date '2026-04-01',
  interval '1 month') AS m;
```

## Cycles

Hierarchies in real data are not always trees. Suppose someone sets Mia's manager to Vic, creating a loop. The earlier root-based anchor (`manager_id IS NULL`) would now find no rows. To demonstrate the cycle, start explicitly at Mia (`WHERE id = 1`); then the recursive term keeps finding rows: Mia, Raj, Tom, Vic, Mia, Raj...

Three defences:

1. **`UNION` instead of `UNION ALL`.** `UNION` discards rows already produced. If the rows are just `(id, name)`, the second Mia is a duplicate and the loop stops (6 rows). But add a `depth` column and every row is unique again, so `UNION` no longer saves you.
2. **Track the path** and refuse to revisit:

```sql
SELECT s.id,
       c.path || s.id || ','
FROM staff s
JOIN chain c
  ON s.manager_id = c.id
WHERE c.path NOT LIKE
      '%,' || s.id || ',%'
```

   with the anchor's path starting as `',1,'`. Postgres users can keep an integer array and test `s.id <> ALL(c.path)`.
3. **Postgres 14+ `CYCLE` clause**, which does the path tracking for you:

```sql
WITH RECURSIVE chain AS (...)
CYCLE id SET is_cycle USING path
SELECT * FROM chain;
```

   On the looped data this returns the six staff plus one extra Mia row with `is_cycle = true`, then stops.

A depth limit (`WHERE c.depth < 20`) is a cheap last line of defence in any database.

## Differences that bite

| Feature | SQLite | Postgres |
|---|---|---|
| `RECURSIVE` keyword | Optional | Required |
| `CYCLE`/`SEARCH` | No | 14+ |
| DML inside `WITH` | No | Yes |
| `generate_series` | No* | Yes |

\* SQLite builds can include a `generate_series` table-valued function as an extension, but don't rely on it being present.

Leaving out `RECURSIVE` in Postgres gives `relation "n" does not exist ... Use WITH RECURSIVE`. SQLite accepts the self-reference anyway, for compatibility with SQL Server and Oracle, which don't use the keyword.

### Data-modifying CTEs (Postgres)

Postgres lets a CTE contain `INSERT`, `UPDATE` or `DELETE` with `RETURNING`, so you can move rows atomically in one statement:

```sql
WITH moved AS (
  DELETE FROM orders
  WHERE ordered_on < '2025-01-01'
  RETURNING *
)
INSERT INTO orders_archive
SELECT * FROM moved;
```

All parts of the statement see the same snapshot, so a `SELECT` elsewhere in the same `WITH` won't see the deletion. SQLite rejects `DELETE` inside `WITH`.

## Key takeaways
- A CTE names an intermediate result so a query reads as a sequence of steps, and can be referenced more than once.
- Postgres 12+ normally inlines a once-referenced, non-recursive, side-effect-free SELECT CTE; repeated references normally materialise. Overrides apply only when eligible.
- A recursive CTE is an anchor plus a recursive term; each pass sees only the previous pass's rows, and stops when a pass adds nothing.
- Always have a termination condition, and protect against cycles with a path check, `UNION`, Postgres's `CYCLE` clause or a depth cap.
- Postgres requires `WITH RECURSIVE`, enforces matching column types, and supports data-modifying CTEs; SQLite does none of these.

## Further reading
- [WITH queries (CTEs) — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-with.html)
- [The WITH clause — SQLite docs](https://www.sqlite.org/lang_with.html)
- [Hierarchical and recursive queries in SQL — Wikipedia](https://en.wikipedia.org/wiki/Hierarchical_and_recursive_queries_in_SQL)
- [Literate SQL with WITH — Modern SQL](https://modern-sql.com/feature/with)
