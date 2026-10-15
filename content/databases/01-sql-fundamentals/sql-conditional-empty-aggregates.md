---
id: sql-conditional-empty-aggregates
title: Count conditions and handle empty input
level: intermediate
minutes: 3
sourceLesson: sql-group-by
summary: CASE and FILTER let different aggregates select different inputs.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## Conditional aggregation

You often want several counts side by side. Put a condition inside the aggregate:

```sql
-- Each aggregate chooses its own input
-- rows.
SELECT
  SUM(CASE WHEN status = 'shipped'
      THEN 1 ELSE 0 END) AS shipped,
  COUNT(*) FILTER
    (WHERE status = 'pending')
    AS pending
FROM orders;
```

| shipped | pending |
|---|---|
| 3 | 2 |

The `CASE` form works because summing 1s and 0s is counting. Each row contributes 1 if it meets the condition and 0 if it doesn't:

```formula
n_s = Σ s_i
n_s = 1 + 1 + 0 + 1 + 0 + 0 = 3
where
n_s: the number of shipped orders
Σ: sigma, "the sum of": add up s_i over every row i
i: one row of orders (101 to 106, in order)
s_i: 1 if row i has status 'shipped', otherwise 0 (what the CASE expression returns)
In words: adding a 1 for every row that passes the test and a 0 for every row that fails it gives the number of rows that pass.
```

The CASE form works in both engines and is widely portable. FILTER is standard SQL; PostgreSQL has supported it since 9.4 and SQLite since 3.30. This one-pass "pivot" avoids issuing a separate query per status and can avoid repeated scans. Actual performance depends on the plan and available indexes.

## Joining strings

To list the names in each group, PostgreSQL has `string_agg(name, ', ' ORDER BY name)`. SQLite has long had `group_concat(name, ', ')` and added `string_agg` with in-aggregate `ORDER BY` in 3.44. Without the `ORDER BY` inside the call, the order of the joined names is unspecified.

## Empty input

What does `SUM(price)` return when no rows match?

```sql
-- No prices match: SUM is NULL, COUNT is
-- zero.
SELECT SUM(price) FROM products
WHERE price > 1000;   -- NULL
SELECT COUNT(*) FROM products
WHERE price > 1000;   -- 0
```

`COUNT` of nothing is 0, but `SUM`, `AVG`, `MIN` and `MAX` of nothing are **NULL**. Wrap them in `COALESCE(SUM(price), 0)` when a report needs a zero. (SQLite also has a non-standard `TOTAL()` that returns 0.0.)

Add `GROUP BY` and the behaviour changes: no rows means no groups, so the query returns **zero rows**, not one row of NULL.

## Key takeaways
- CASE and FILTER let different aggregates select different inputs.
- Specify ordering inside string aggregation when name order matters.
- An ungrouped empty input still gives one aggregate row; GROUP BY gives no groups.

## Further reading
- [Aggregate functions — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Built-in aggregate functions — SQLite documentation](https://www.sqlite.org/lang_aggfunc.html)
- [Aggregate expressions and FILTER — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-AGGREGATES)
