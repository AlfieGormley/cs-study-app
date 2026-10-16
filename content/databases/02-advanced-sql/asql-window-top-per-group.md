---
id: asql-window-top-per-group
title: Keeping the latest row per group
level: intermediate
minutes: 3
summary: Compute window values before filtering them in an outer query.
sourceLesson: asql-window-functions
---

The shop has eight orders across four ordering customers. A window function leaves rows in place. PARTITION BY customer_id restarts the calculation for each customer, and ORDER BY inside OVER sets the window order.

## Top-N per group

The most common real use of `ROW_NUMBER`: each customer's latest order.

```sql
-- Rank before filtering the result.
SELECT cust, id, ordered_on
FROM (
  SELECT customer_id AS cust, id,
    ordered_on,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY ordered_on DESC, id DESC
    ) AS rn
  FROM orders
) AS t
WHERE rn = 1;
```

| cust | id | ordered_on |
|---|---|---|
| 1 | 107 | 2026-03-15 |
| 2 | 106 | 2026-03-02 |
| 3 | 108 | 2026-03-28 |
| 4 | 105 | 2026-02-20 |

Why the wrapping subquery? Because window functions are computed *after* `WHERE`. Writing `WHERE ROW_NUMBER() OVER (...) = 1` fails in both databases (Postgres says `window functions are not allowed in WHERE`). Some warehouses (Snowflake, BigQuery, DuckDB) add a `QUALIFY` clause for exactly this; SQLite and Postgres do not.

Choose the function to match the business rule: `ROW_NUMBER` returns exactly one row per group even on ties, while `RANK() ... = 1` returns all tied rows.

The secondary id sort chooses a repeatable winner if two latest orders share a date. It does not mean ids encode event time: the date remains the primary rule. To return every order tied on the latest date, rank by date alone; adding id would make those rows cease to be peers. Customers without orders are absent from this input and never get a row number. Start from customers and use a separate outer join if the report must include Eve.

The inner query computes all candidate rankings before the outer filter is applied logically. That separation explains correctness but does not require a physically stored intermediate table; the optimiser can combine or simplify operations while preserving results.

## Key takeaways
- Compute window values before filtering them in an outer query.
- Use ROW_NUMBER for one row and RANK for every tied winner.

## Further reading
- [PostgreSQL 18: tutorial window](https://www.postgresql.org/docs/18/tutorial-window.html)
- [PostgreSQL 18: functions window](https://www.postgresql.org/docs/18/functions-window.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
