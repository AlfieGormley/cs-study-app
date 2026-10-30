---
id: asql-set-precedence
title: Portable grouping of mixed set operators
level: intermediate
minutes: 3
summary: PostgreSQL binds INTERSECT more tightly; SQLite evaluates left to right.
sourceLesson: asql-set-ops-pivot
---

UNION keeps rows found on either side; INTERSECT keeps rows present on both sides. These operators remove duplicates. Mixing them without explicit grouping can change the answer between engines.

## The precedence trap

What does this return?

```sql
-- Engine precedence changes grouping.
SELECT 1
UNION SELECT 2
INTERSECT SELECT 3;
```

| Database | Parses as | Result |
|---|---|---|
| Postgres | INTERSECT first | `1` |
| SQLite | UNION first | empty |

PostgreSQL intersects 2 with 3 first, finds nothing in common, and unions the empty result with 1, leaving 1. SQLite unions 1 and 2 first, and nothing in {1, 2} equals 3, so the result is empty.

The SQL standard (followed by Postgres and SQL Server) gives `INTERSECT` **higher precedence** than `UNION` and `EXCEPT`, the way `*` binds tighter than `+`. SQLite evaluates compound selects strictly left to right. The two documented precedence rules give different answers.

> [!tip] Don't rely on precedence
> When mixing operators, make the order explicit. Postgres allows parentheses around whole queries; SQLite doesn't, so use subqueries: `SELECT * FROM (... UNION ...) INTERSECT ...`.

## Key takeaways
- PostgreSQL binds INTERSECT more tightly; SQLite evaluates left to right.
- A derived table makes the desired grouping portable.

## Further reading
- [PostgreSQL 18: queries union](https://www.postgresql.org/docs/18/queries-union.html)
- [PostgreSQL 18: queries table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_select.html)
