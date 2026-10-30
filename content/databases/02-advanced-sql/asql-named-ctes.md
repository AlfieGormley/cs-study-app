---
id: asql-named-ctes
title: Naming and inspecting intermediate results
level: intermediate
minutes: 3
summary: An ordinary SELECT CTE names an intermediate result within one statement.
sourceLesson: asql-ctes
---

The shop orders total 650: Ana 240, Ben 135, Cat 230 and Dev 45. Eve has none. Monthly revenue is January 165, February 305 and March 180.

A **common table expression** (CTE) is a named subquery written up front with `WITH`. An ordinary SELECT CTE provides a reusable name for a subquery and changes how a query *reads*: top to bottom, one step at a time, instead of inside out.

Recursive CTEs are different. They add something plain SQL can't otherwise express: a query that refers to its own output, which lets you walk trees and graphs of unknown depth.

This unit uses customers and orders from the Advanced SQL fixture. The later hierarchy unit introduces staff.

## The basic shape

```sql
-- Name a result used in later steps.
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

Spend per customer is Ana 240, Ben 135, Cat 230 and Dev 45. The scalar subquery averages those four figures (650 / 4 = 162.5), and only Ana and Cat are above it.

Eve never ordered, so she has no row in `spend` and isn't counted: the average is per ordering customer, not per customer. Notice that `spend` is used twice, once in `FROM` and once in the subquery. With separate derived tables for those two uses, you would repeat the aggregation text. A window aggregate is another possible formulation.

You can chain several CTEs, each able to use the ones before it:

```sql
-- Name a result used in later steps.
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

## Key takeaways
- An ordinary SELECT CTE names an intermediate result within one statement.
- The average over spend counts ordering customers, excluding customers absent from spend.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
