---
id: sql-logical-order-arithmetic
title: Reason about aliases and SQL arithmetic
level: basic
minutes: 3
sourceLesson: sql-select-basics
summary: Logical clause order explains which aliases are visible.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## The order a query is evaluated in

You write clauses in one order, but the database evaluates them, logically, in another:

```flow
FROM: pick the table(s)
WHERE: filter rows
GROUP BY: form groups
HAVING: filter groups
SELECT: compute columns and aliases
DISTINCT: remove duplicates
ORDER BY: sort
LIMIT: cut
```

This explains several rules at once:

- `ORDER BY` can use a `SELECT` alias, because it runs after `SELECT`.
- `WHERE` cannot, in standard SQL, because it runs before `SELECT`. In PostgreSQL, `WHERE double_price > 60` fails with `column "double_price" does not exist`. SQLite is lenient and accepts it, which is another way a query can work in tests and fail in production. Repeat the expression instead: `WHERE price * 2 > 60`.
- `LIMIT` applies to the sorted result, so "top 3" queries work as expected.

This is the **logical** order. The optimiser may physically do things differently, for example by using an index to read rows already sorted, but the result must be the same as if it had followed these steps.

## Arithmetic surprises

`SELECT 7/2` returns `3`, not `3.5`, in both SQLite and PostgreSQL: dividing two integers gives an integer. The digits after the decimal point are dropped, which moves the result towards zero, so `-7/2` is `-3`. The `%` operator gives back what was left over: `7 % 2` is `1`.

```sql
-- Integer division truncates; % is the
-- remainder.
SELECT 7/2, -7/2, 7 % 2, 7/2.0;
-- SQLite: 3 | -3 | 1 | 3.5
-- PostgreSQL shows the last value as
-- numeric: 3.5000000000000000
```

These small integer examples assume a nonzero divisor and a representable result. PostgreSQL raises an error on integer overflow; SQLite can promote overflowing arithmetic to floating point.

Because the result is truncated rather than rounded, `SELECT 9/10` is 0, not 1. Write `7/2.0` or `CAST(x AS REAL)` (PostgreSQL: `x::numeric`) when you want a fraction: one non-integer operand makes the whole division non-integer.

String concatenation uses `||`: `name || ' (' || city || ')'` gives `Asha (London)`. For Chloe it gives NULL, because this operator propagates a NULL operand in SQLite and PostgreSQL. Other functions, such as COALESCE and concat, have different rules; the NULL units explain them.

## Key takeaways
- Logical clause order explains which aliases are visible.
- Integer division truncates towards zero in SQLite and PostgreSQL.
- The || concatenation operator propagates NULL in these engines.

## Further reading
- [SELECT — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-select.html)
- [Quirks, caveats and gotchas in SQLite](https://www.sqlite.org/quirks.html)
