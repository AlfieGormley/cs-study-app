---
id: asql-dynamic-unpivot
title: Dynamic report columns and unpivoting
level: intermediate
minutes: 3
summary: A static PostgreSQL or SQLite SELECT has a fixed output shape.
sourceLesson: asql-set-ops-pivot
---

Pivoting turns category values into columns. Unpivoting turns columns into rows. These are changes to report shape, so first decide whether a consumer really needs a wide table or can accept named metric rows.

### Dynamic pivots

In PostgreSQL and SQLite, a static pivot has fixed output columns. Generating "one column per category, whatever categories exist" therefore needs an additional step. Other engines may offer dynamic-pivot syntax. Options:

- Generate the SQL in application code after querying the distinct values.
- Postgres's `tablefunc` extension provides `crosstab()`, but you still declare the output columns.
- SQL Server and Oracle have a `PIVOT` operator, also with a fixed column list.
- Often best: return long (unpivoted) rows and pivot in the reporting tool or with pandas `pivot_table`.

## Unpivoting: columns to rows

The reverse turns a wide row into several narrow ones. The portable way is `UNION ALL`:

```sql
-- Emit one row per chosen metric.
SELECT id, 'total' AS metric,
       total AS val
FROM orders
UNION ALL
SELECT id, 'cust', customer_id
FROM orders;
```

The straightforward plan scans the table once per branch; inspect the actual plan. Postgres can do it in one pass with `LATERAL` and `VALUES`:

```sql
-- Emit one row per chosen metric.
SELECT o.id, k.metric, k.val
FROM orders o
CROSS JOIN LATERAL (VALUES
  ('total', o.total),
  ('cust', o.customer_id)
) AS k(metric, val);
```

`LATERAL` lets a subquery in `FROM` refer to columns of tables to its left. SQLite doesn't support it.

LATERAL explains the scope of each expression: for one outer order row, the VALUES list makes a total metric and a customer metric from that row. Eight orders therefore produce sixteen metric rows. No ORDER BY is present, so their display order is unspecified. The val column must have a common type; these two source columns are integers. For unrelated types, choose a deliberate representation rather than relying on an accidental cast.

When generating a dynamic pivot, category names become SQL identifiers rather than bound data values. Use the database driver’s identifier-quoting facilities, keep values parameterised, and keep the report’s output contract clear. Returning long rows avoids rebuilding a query whenever a category is added.

## Key takeaways
- A static PostgreSQL or SQLite SELECT has a fixed output shape.
- UNION ALL unpivots portably; PostgreSQL LATERAL can reference an earlier FROM item.

## Further reading
- [PostgreSQL 18: queries union](https://www.postgresql.org/docs/18/queries-union.html)
- [PostgreSQL 18: queries table expressions](https://www.postgresql.org/docs/18/queries-table-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_select.html)
