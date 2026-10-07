---
id: sql-null
title: NULL semantics
level: intermediate
minutes: 13
summary: NULL means unknown, not empty. Three-valued logic, why = NULL never matches, the NOT IN trap, and how NULL behaves in aggregates, sorting, constraints and joins.
---

NULL is the part of SQL that most often makes a correct-looking query return the wrong rows. The rules are consistent once you hold one idea: **NULL means "unknown"**, not zero, not an empty string, and not "nothing".

If Chloe's city is unknown, is she in London? We don't know. Is she *not* in London? We don't know that either. SQL encodes that "don't know" as a third truth value, **UNKNOWN**, alongside TRUE and FALSE.

The shop schema has three kinds of NULL that this lesson uses: Chloe's `city`, the `referred_by` of Asha and Erin, and the `customer_id` of guest order 106.

## Comparisons with NULL are unknown

Any ordinary comparison involving NULL gives UNKNOWN (SQL shows it as NULL):

```sql
SELECT NULL = NULL,   -- NULL
       NULL <> 1,     -- NULL
       NULL + 1,      -- NULL
       'a' || NULL;   -- NULL
```

Even `NULL = NULL` is unknown: two unknown values might or might not be equal. So this finds nobody:

```sql
SELECT name FROM customers
WHERE city = NULL;     -- 0 rows
```

Use the dedicated predicates instead:

```sql
WHERE city IS NULL       -- Chloe
WHERE city IS NOT NULL   -- other 4
```

## Three-valued logic

`AND`, `OR` and `NOT` extend naturally. Treat UNKNOWN as "could be either" and ask whether the answer would change:

| AND | T | F | U |
|---|---|---|---|
| **T** | T | F | U |
| **F** | F | F | F |
| **U** | U | F | U |

| OR | T | F | U |
|---|---|---|---|
| **T** | T | T | T |
| **F** | T | F | U |
| **U** | T | U | U |

`NOT U` is U. The short-cuts are worth memorising: `FALSE AND anything` is FALSE, and `TRUE OR anything` is TRUE. In both cases the unknown side can't change the result.

### WHERE keeps only TRUE

This is the rule that turns three-valued logic into missing rows. `WHERE`, `HAVING` and join `ON` conditions keep a row only if the condition is **TRUE**. FALSE and UNKNOWN are both thrown away.

```sql
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

`WHERE city IS DISTINCT FROM 'London'` returns Ben, Chloe and Erin. PostgreSQL has supported it for many years. SQLite added it in 3.39, and has long had its own shorter spelling: `IS` and `IS NOT` work with any value, so `city IS NOT 'London'` means the same thing. PostgreSQL's `IS` only accepts `NULL`, `TRUE`, `FALSE` and `UNKNOWN` after it.

`IS NOT DISTINCT FROM` is the NULL-safe equality. It is handy for comparing two nullable columns, for example when checking whether a row has changed.

## The NOT IN trap

This query looks like "customers who have never ordered":

```sql
SELECT name FROM customers
WHERE id NOT IN (
  SELECT customer_id FROM orders);
```

It returns **no rows at all**, even though Erin has never ordered. The reason is the guest order's NULL `customer_id`. The subquery produces (1, 1, 2, 3, 4, NULL), and `x NOT IN (list)` expands to:

```
x <> 1 AND x <> 1 AND x <> 2
AND x <> 3 AND x <> 4 AND x <> NULL
```

For Erin (id 5), every comparison is TRUE except the last, which is UNKNOWN. `TRUE AND UNKNOWN` is UNKNOWN, so `WHERE` drops her. For everyone else one comparison is FALSE. One NULL in the list and `NOT IN` can never be TRUE.

`IN` has no such problem. `3 IN (1, NULL)` is UNKNOWN, but `1 IN (1, NULL)` is TRUE, so positive matches still work. The trap is specific to the negation.

The fix is `NOT EXISTS`, which asks whether a matching row exists, a question that is always TRUE or FALSE:

```sql
SELECT name FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.id);
-- Erin
```

The `LEFT JOIN ... WHERE o.id IS NULL` anti-join from the joins lesson also works. Adding `WHERE customer_id IS NOT NULL` to the subquery fixes `NOT IN` too, but it is easy to forget, and the bug only appears once the first NULL arrives in production. Prefer `NOT EXISTS` by habit. PostgreSQL's planner also handles `NOT EXISTS` well (as an anti-join), while it often can't turn `NOT IN` over a subquery into one, precisely because of these NULL rules.

## Functions that tame NULL

`COALESCE(a, b, ...)` returns the first argument that isn't NULL:

```sql
SELECT name,
  COALESCE(city, 'unknown') AS city
FROM customers;
```

That shows Chloe's city as `unknown`. `NULLIF(a, b)` does the reverse: it returns NULL when `a = b`, otherwise `a`. Its classic use is avoiding division by zero. `total / NULLIF(n, 0)` returns NULL instead of failing when `n` is 0. PostgreSQL raises `division by zero`; SQLite already returns NULL, so the guard matters most for portability.

String concatenation with `||` is NULL if either side is NULL. PostgreSQL's `concat()` function skips NULL arguments instead (`concat('a', NULL)` is `'a'`), and SQLite added the same function in 3.44.

### CASE and NULL

A searched `CASE` follows the WHERE rule: a branch is taken only if its condition is TRUE.

```sql
CASE WHEN city = 'London'  THEN 'local'
     WHEN city <> 'London' THEN 'away'
     ELSE '?' END
```

Chloe falls through both branches to `'?'`. The simple form, `CASE city WHEN NULL THEN ...`, compares with `=`, so its NULL branch can **never** match. Write `CASE WHEN city IS NULL THEN ...` instead.

## NULL in aggregates

`SUM`, `AVG`, `MIN`, `MAX` and `COUNT(column)` skip NULLs. This is not universal: PostgreSQL `array_agg` includes NULL elements. That is usually what you want, but it changes what an average means. Suppose we add a `rating` column where only three products have been rated:

| name | rating |
|---|---|
| Kettle | 5 |
| Toaster | 3 |
| Lamp | NULL |
| Rug | NULL |
| Mug | 4 |

| expression | result |
|---|---|
| `AVG(rating)` | 4.0 |
| `SUM(rating)*1.0/COUNT(*)` | 2.4 |
| `AVG(COALESCE(rating, 0))` | 2.4 |

`AVG` is 12 / 3: the mean of the ratings we know. Treating unrated products as 0 gives 12 / 5. Neither is wrong, but they answer different questions, so decide which one you mean. Replacing NULL with 0 is a claim that the value is zero, and it is often false.

Recall from the previous lesson that `SUM` over no rows returns NULL, not 0.

## Grouping, DISTINCT and sorting

Here SQL switches rules. For grouping and duplicate removal, NULLs are treated as **equal to each other**:

- `SELECT DISTINCT referred_by` gives NULL, 1, 2: one NULL, not two.
- `GROUP BY city` puts all NULL cities in one group.

For sorting, NULLs are treated as either smaller or larger than every value. As lesson 1 showed, SQLite puts them **first** in ascending order and PostgreSQL puts them **last**. `NULLS FIRST` and `NULLS LAST` make it explicit.

`MIN` and `MAX` ignore NULLs: `MIN(city)` is Bristol, not NULL.

## NULL in constraints

Constraints also lean towards letting NULL through.

**UNIQUE** allows many NULLs. Two rows with a NULL email don't violate `email UNIQUE`, because neither is known to equal the other. Both SQLite and PostgreSQL behave this way by default. PostgreSQL 15 added `UNIQUE NULLS NOT DISTINCT` for when you want at most one NULL.

**CHECK** fails only when the condition is FALSE. With `age INTEGER CHECK (age >= 18)`, inserting age 10 fails, but inserting NULL succeeds, because `NULL >= 18` is UNKNOWN, not FALSE. Add `NOT NULL` when the value is required:

```sql
age INTEGER NOT NULL
    CHECK (age >= 18)
```

This asymmetry, where WHERE rejects UNKNOWN but CHECK accepts it, catches people out. Both follow the same principle: only reject on evidence.

## NULLs from outer joins

A `LEFT JOIN` fills unmatched right-hand columns with NULL. Filtering on those columns in `WHERE` quietly turns the outer join back into an inner one:

```sql
SELECT c.name, r.name AS ref
FROM customers c
LEFT JOIN customers r
  ON r.id = c.referred_by
WHERE r.city <> 'Leeds';
```

| name | ref |
|---|---|
| Ben | Asha |
| Chloe | Asha |

Asha and Erin have no referrer, so `r.city` is NULL, the test is UNKNOWN and they vanish. Dev's referrer is Ben, from Leeds. If you meant "keep everyone, but only show referrers outside Leeds", move `r.city <> 'Leeds'` into `ON`. Replacing the `WHERE` condition with `r.city IS DISTINCT FROM 'Leeds'` keeps unmatched rows but still removes Dev, whose referrer is in Leeds; it does not preserve everyone.

## Design advice

- Use `NOT NULL` by default and allow NULL only where "unknown" or "not applicable" is a real state. Every nullable column makes every query on it harder to reason about.
- Don't invent stand-in values such as `''`, `0` or `1900-01-01` for unknown. They take part in comparisons and aggregates as if they were real.
- When a column is nullable, ask for each query: what happens to the NULL rows here?

## Key takeaways
- NULL means unknown. Comparisons with it give UNKNOWN, and `WHERE` keeps only TRUE rows.
- Use `IS NULL`, never `= NULL`. Use `IS DISTINCT FROM` (or SQLite's `IS NOT`) for NULL-safe comparison.
- One NULL in a `NOT IN` list makes it return nothing. Use `NOT EXISTS`.
- Common numeric aggregates skip NULLs; `AVG` averages known values only. `COUNT(*)` counts rows, and some collection aggregates retain NULLs.
- `DISTINCT` and `GROUP BY` treat NULLs as one value; sort order of NULL differs between SQLite and PostgreSQL.
- UNIQUE allows many NULLs, and CHECK passes on NULL. Pair constraints with `NOT NULL`.

## Further reading
- [Null (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Null_(SQL))
- [Comparison functions and operators — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-comparison.html)
- [Subquery expressions (NOT IN, EXISTS) — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-subquery.html)
- [NULL handling in SQLite versus other database engines](https://www.sqlite.org/nulls.html)
- [Three-valued logic — Modern SQL](https://modern-sql.com/concept/three-valued-logic)
