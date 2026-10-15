---
id: sql-null-safe-comparison
title: Filter unknowns and compare nullable values
level: intermediate
minutes: 3
sourceLesson: sql-null
summary: WHERE keeps TRUE and discards FALSE and UNKNOWN.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

### WHERE keeps only TRUE

This is the rule that turns three-valued logic into missing rows. `WHERE` and `HAVING` retain only rows or groups whose condition is **TRUE**. An `ON` condition produces a matching pair only when TRUE; an outer join can subsequently preserve unmatched rows by padding. FALSE and UNKNOWN do not satisfy any of these conditions.

```sql
-- Unknown cities do not pass this
-- predicate.
SELECT name FROM customers
WHERE city <> 'London';
```

| name |
|---|
| Ben |
| Erin |

Chloe disappears. For her, `NULL <> 'London'` is UNKNOWN. Worse, `WHERE NOT (city = 'London')` gives the same two rows, because `NOT UNKNOWN` is still UNKNOWN. A row can fail both a condition and its negation. Together, `city = 'London'` and `city <> 'London'` cover only four of the five customers.

If you want Chloe included, say so:

```sql
-- WHERE fragment: include unknown cities
-- too.
WHERE city <> 'London'
   OR city IS NULL
```

### IS DISTINCT FROM

The standard has a NULL-safe comparison that treats NULL as an ordinary, comparable value:

| a | b | `a <> b` | `a IS DISTINCT FROM b` |
|---|---|---|---|
| 1 | 2 | T | T |
| 1 | 1 | F | F |
| 1 | NULL | U | T |
| NULL | NULL | U | F |

`WHERE city IS DISTINCT FROM 'London'` returns Ben, Chloe and Erin. PostgreSQL has supported it for many years. SQLite added it in 3.39, and has long had its own shorter spelling: `IS` and `IS NOT` also compare ordinary values, so `city IS NOT 'London'` means the same thing here. Boolean literals on the right of SQLite IS have special truth-testing rules. In PostgreSQL, write `IS DISTINCT FROM` or `IS NOT DISTINCT FROM` to compare arbitrary values; the separate predicates `IS NULL`, `IS TRUE`, `IS FALSE` and `IS UNKNOWN` test missingness or truth.

`IS NOT DISTINCT FROM` is the NULL-safe equality. It is handy for comparing two nullable columns, for example when checking whether a row has changed. In SQLite, the boolean-literal exception also applies to the long spelling: `2 IS NOT DISTINCT FROM TRUE` is true, because it tests truthiness; PostgreSQL rejects this integer-versus-boolean comparison. For the nullable text columns here, both spellings perform the intended value comparison.

## Key takeaways
- WHERE keeps TRUE and discards FALSE and UNKNOWN.
- Add an explicit IS NULL branch when unknown values should pass.
- IS DISTINCT FROM detects changes involving NULL.

## Further reading
- [Comparison functions and operators — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-comparison.html)
- [NULL handling in SQLite versus other database engines](https://www.sqlite.org/nulls.html)
