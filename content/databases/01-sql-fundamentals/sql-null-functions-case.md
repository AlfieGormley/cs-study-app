---
id: sql-null-functions-case
title: Choose fallback values and CASE branches
level: intermediate
minutes: 3
sourceLesson: sql-null
summary: COALESCE returns the first non-NULL argument.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## Functions that tame NULL

`COALESCE(a, b, ...)` returns the first argument that isn't NULL:

```sql
-- Supply display text for the missing city.
SELECT name,
  COALESCE(city, 'unknown') AS city
FROM customers;
```

That shows Chloe's city as `unknown`. `NULLIF(a, b)` does the reverse: it returns NULL when `a = b`, otherwise `a`. Its classic use is avoiding division by zero. `total / NULLIF(n, 0)` returns NULL instead of failing when `n` is 0. PostgreSQL raises `division by zero`; SQLite already returns NULL, so the guard matters most for portability.

String concatenation with `||` is NULL if either side is NULL. PostgreSQL's `concat()` function skips NULL arguments instead (`concat('a', NULL)` is `'a'`), and SQLite added the same function in 3.44.

### CASE and NULL

A searched `CASE` follows the WHERE rule: a branch is taken only if its condition is TRUE.

```sql
-- SELECT expression, followed by FROM
-- customers.
CASE WHEN city = 'London'  THEN 'local'
     WHEN city <> 'London' THEN 'away'
     ELSE '?' END
```

Chloe falls through both branches to `'?'`. The simple form, `CASE city WHEN NULL THEN ...`, compares with `=`, so its NULL branch can **never** match. Write `CASE WHEN city IS NULL THEN ...` instead.

## Key takeaways
- COALESCE returns the first non-NULL argument.
- NULLIF can turn a zero divisor into NULL.
- Use searched CASE with IS NULL to handle missing values.

## Further reading
- [Conditional expressions: CASE, COALESCE and NULLIF — PostgreSQL](https://www.postgresql.org/docs/current/functions-conditional.html)
- [Built-in scalar functions — SQLite](https://www.sqlite.org/lang_corefunc.html)
- [Comparison functions and operators — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-comparison.html)
- [NULL handling in SQLite versus other database engines](https://www.sqlite.org/nulls.html)
