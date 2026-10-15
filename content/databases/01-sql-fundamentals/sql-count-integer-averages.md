---
id: sql-count-integer-averages
title: Count rows and avoid truncated averages
level: intermediate
minutes: 3
sourceLesson: sql-group-by
summary: COUNT(*) counts rows; COUNT(column) counts known values.
---

The shop has six orders: five known customer ids (1, 1, 2, 3, 4) and one guest NULL. Its nine order lines contain fourteen items in total. Prices are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8.

### Three kinds of COUNT

`COUNT` is the one people trip over, because it has three forms that answer different questions:

```sql
-- Contrast all, known and distinct known
-- ids.
SELECT COUNT(*),
       COUNT(customer_id),
       COUNT(DISTINCT customer_id)
FROM orders;
```

| form | result | counts |
|---|---|---|
| `COUNT(*)` | 6 | rows |
| `COUNT(customer_id)` | 5 | non-NULL values |
| `COUNT(DISTINCT ...)` | 4 | distinct non-NULL values |

Guest order 106 has a NULL `customer_id`, so `COUNT(customer_id)` skips it. Asha placed two orders, so the distinct count drops to 4. The numeric aggregates shown here, along with `COUNT(column)`, ignore NULLs; the NULL units looks at what that means for averages.

### Integer arithmetic

`SUM` of integers is an integer, and dividing two integers truncates. `SUM(qty) / COUNT(*)` over `order_items` divides the 14 items by the 9 lines:

```formula
q = trunc(a / b)
q = trunc(14 / 9) = trunc(1.555…) = 1
where
q: the result of dividing integer a by integer b in SQLite or PostgreSQL
a: the dividend, here SUM(qty) = 14 items
b: the divisor, here COUNT(*) = 9 order lines
trunc: truncate: drop everything after the decimal point, moving towards zero, so trunc(1.9) = 1
…: the digits carry on repeating (1.5555…)
In words: when both sides are integers, the answer keeps only the whole-number part, so 14 / 9 gives 1, not 1.56.
```

`AVG(qty)` gives 1.555... instead. Use `AVG`, or multiply by `1.0` first (`SUM(qty) * 1.0 / COUNT(*)`), so the division is no longer between two integers.

PostgreSQL differs in a useful way here: `AVG` of an integer column returns `numeric`, so you see `38.6000000000000000` rather than SQLite's floating-point `38.6`. `SUM` of an `integer` column returns `bigint`, which widens the range but can still overflow at the 64-bit limit.

## Key takeaways
- COUNT(*) counts rows; COUNT(column) counts known values.
- COUNT(DISTINCT column) counts distinct non-NULL values.
- AVG avoids the truncation of integer SUM divided by integer COUNT.

## Further reading
- [Aggregate functions — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Built-in aggregate functions — SQLite documentation](https://www.sqlite.org/lang_aggfunc.html)
