---
id: asql-data-changing-ctes
title: Changing data with CTEs
level: intermediate
minutes: 3
summary: PostgreSQL data-modifying CTEs communicate changed rows through RETURNING.
sourceLesson: asql-ctes
---

An ordinary common table expression (CTE) names a SELECT result for one statement. PostgreSQL also allows data modification in WITH; SQLite only allows SELECT bodies there. Examples use orders, order_items and a matching orders_archive table.

## Differences that bite

| Feature | SQLite | Postgres |
|---|---|---|
| `RECURSIVE` modifier | Optional | Required |
| CYCLE clause / SEARCH clause | No | 14+ |
| DML inside `WITH` | No | Yes |
| `generate_series` | No* | Yes |

\* SQLite builds can include a `generate_series` table-valued function as an extension, but don't rely on it being present.

Leaving out `RECURSIVE` in Postgres gives `relation "n" does not exist ... Use WITH RECURSIVE`. SQLite accepts the recursive self-reference anyway, for compatibility with SQL Server and Oracle, which don't use that modifier.

### Data-modifying CTEs (Postgres)

Postgres lets a CTE contain `INSERT`, `UPDATE` or `DELETE` with `RETURNING`, so you can move rows atomically in one statement:

```sql
-- Transfer DELETE output via RETURNING.
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
- PostgreSQL data-modifying CTEs communicate changed rows through RETURNING.
- Sibling statements share a snapshot and cannot observe one another’s table changes.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
