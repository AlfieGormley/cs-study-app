---
id: sql-select-basics
title: SELECT, WHERE and ORDER BY
level: basic
minutes: 12
summary: Reading data with SQL. Pick columns, filter rows, sort and page through them, and learn the order in which a query is actually evaluated.
---

SQL is a **declarative** language. You describe the rows you want and the database works out how to fetch them. You never write a loop. That is why one short query can replace fifty lines of Python, and also why small slips in a query can quietly give you the wrong answer.

Every lesson in this module uses the same small shop database. Learn its shape once and the examples will make sense straight away.

## The example schema

```
customers(id, name, city, referred_by)
products(id, name, price, category)
orders(id, customer_id, ordered_on, status)
order_items(order_id, product_id, qty)
```

| customers | city | referred_by |
|---|---|---|
| 1 Asha | London | NULL |
| 2 Ben | Leeds | 1 |
| 3 Chloe | NULL | 1 |
| 4 Dev | London | 2 |
| 5 Erin | Bristol | NULL |

| products | price | category |
|---|---|---|
| 1 Kettle | 30 | kitchen |
| 2 Toaster | 25 | kitchen |
| 3 Lamp | 40 | home |
| 4 Rug | 90 | home |
| 5 Mug | 8 | NULL |

| orders | customer | date / status |
|---|---|---|
| 101 | 1 | 2026-01-05 shipped |
| 102 | 1 | 2026-02-11 shipped |
| 103 | 2 | 2026-02-14 pending |
| 104 | 3 | 2026-03-02 shipped |
| 105 | 4 | 2026-03-09 cancelled |
| 106 | NULL | 2026-03-10 pending |

`order_items` links orders to products with a quantity, for example (101, Kettle, 1) and (101, Mug, 4). Prices are whole pounds to keep the arithmetic easy. Order 106 is a guest checkout with no customer, Erin has never ordered, and nobody has bought the Rug. Those gaps matter in later lessons.

Result tables illustrate the expected SQLite behaviour of the small shop examples. Differences from PostgreSQL are called out.

> [!note] Content gap: execution provenance
> The original claim that every result table was captured from an executed query could not be substantiated from a reproducible record in this project. That execution claim is omitted; the audit report identifies the examples independently checked.

## SELECT and FROM

The smallest useful query names some columns and a table:

```sql
SELECT name, price
FROM products;
```

`SELECT *` returns every column. It is handy at the prompt but a bad habit in application code: adding a column to the table silently changes what your code receives, and you pull more data than you need.

You can compute new columns and name them with `AS`:

```sql
SELECT name, price * 2 AS double_price
FROM products;
```

The name after `AS` is an **alias**. Strings use **single quotes**: `'London'`. Double quotes are for identifiers, such as a column called `"order"` that clashes with a keyword.

> [!warning] Double quotes in SQLite
> When legacy double-quoted-string compatibility is enabled, SQLite has a quirk: if `"London"` is not a column name, it treats it as the string `'London'`. PostgreSQL raises `column "London" does not exist`. Worse, `WHERE city = "city"` in SQLite compares the column with itself. Always use single quotes for strings.

## WHERE: filtering rows

`WHERE` keeps only the rows for which a condition is true.

```sql
SELECT name, price
FROM products
WHERE price > 25
ORDER BY price DESC;
```

| name | price |
|---|---|
| Rug | 90 |
| Lamp | 40 |
| Kettle | 30 |

The comparison operators are `=`, `<>` (or `!=`), `<`, `<=`, `>` and `>=`. Combine conditions with `AND`, `OR` and `NOT`. A few shorthands save typing:

| Shorthand | Means |
|---|---|
| `x IN ('a','b')` | `x = 'a' OR x = 'b'` |
| `x BETWEEN 25 AND 40` | `x >= 25 AND x <= 40` |
| `name LIKE 'K%'` | starts with K |
| `name LIKE '_ug'` | any one char, then ug |

`BETWEEN` includes **both** ends. `%` in a `LIKE` pattern matches any run of characters (including none) and `_` matches exactly one, so `'_ug'` finds Rug and Mug.

### AND binds tighter than OR

This is the most common filtering bug. Suppose you want kitchen or home products over £50:

```sql
SELECT name, price FROM products
WHERE category = 'kitchen'
   OR category = 'home' AND price > 50;
```

| name | price |
|---|---|
| Kettle | 30 |
| Toaster | 25 |
| Rug | 90 |

`AND` is evaluated first, so this means "kitchen (any price), or home over £50". Kettle and Toaster sneak in. Brackets fix it:

```sql
WHERE (category = 'kitchen'
       OR category = 'home')
  AND price > 50;
```

Now only Rug is returned. When a condition mixes `AND` and `OR`, always add brackets, even when you know the precedence. The next reader may not.

### Case sensitivity differs

`'Kettle' = 'kettle'` is false in both databases. `LIKE` is not consistent:

- In **SQLite**, `LIKE` ignores case for ASCII letters by default, so `name LIKE 'k%'` finds Kettle.
- In **PostgreSQL**, `LIKE` is case-sensitive with a deterministic case-sensitive collation; PostgreSQL 18 also supports `LIKE` with nondeterministic collations such as case-insensitive ones. Use `ILIKE`, or `lower(name) LIKE 'k%'`.

Moving a query from SQLite in tests to PostgreSQL in production can therefore change its results.

### Dates as text

SQLite has no date type. This schema stores ISO-8601 text like `'2026-02-14'`, which sorts and compares correctly as a string. Watch the upper bound once times appear, though:

```sql
SELECT '2026-02-28 14:00'
  BETWEEN '2026-02-01' AND '2026-02-28';
-- 0 (false)
```

The string with a time comes after `'2026-02-28'`, so the last afternoon of February falls outside the range. The robust pattern is a **half-open range**, which works the same for PostgreSQL `date` and `timestamp` columns:

```sql
WHERE ordered_on >= '2026-02-01'
  AND ordered_on <  '2026-03-01'
```

## ORDER BY: sorting

**Without `ORDER BY`, row order is not guaranteed.** It often looks stable on a small table, then changes after an index is added, the table grows or the planner picks a parallel plan. If order matters, say so.

```sql
SELECT name, category, price
FROM products
ORDER BY category, price DESC;
```

| name | category | price |
|---|---|---|
| Mug | NULL | 8 |
| Rug | home | 90 |
| Lamp | home | 40 |
| Kettle | kitchen | 30 |
| Toaster | kitchen | 25 |

Rows are sorted by `category` first and `price DESC` breaks ties within a category. `DESC` applies only to the column it follows; `category` is still ascending.

> [!note] Where do NULLs sort?
> SQLite treats NULL as smaller than any value, so NULLs come **first** in ascending order. PostgreSQL treats NULL as larger, so they come **last**. Both accept `ORDER BY category NULLS LAST` (SQLite since 3.30) if you need the same result everywhere.

You can also sort by an alias (`ORDER BY double_price`) or a column position (`ORDER BY 2`). Positions are fragile: reorder the select list and the sort silently changes.

## DISTINCT

`SELECT DISTINCT city FROM customers` removes duplicate rows from the result: London, Leeds, Bristol and one NULL. `DISTINCT` applies to the **whole row**, not one column. `SELECT DISTINCT city, name` would return all five customers, because every (city, name) pair is unique.

Reaching for `DISTINCT` to hide duplicates you did not expect is a warning sign. The duplicates usually come from a join that multiplies rows (next lesson), and the real fix is the join.

## LIMIT and OFFSET

`LIMIT` caps the number of rows and `OFFSET` skips some first:

```sql
SELECT name, price FROM products
ORDER BY price DESC
LIMIT 2 OFFSET 1;
```

| name | price |
|---|---|
| Lamp | 40 |
| Kettle | 30 |

Two rules:

1. `LIMIT` without a deterministic `ORDER BY` returns an arbitrary set of rows. If two rows tie on the sort key, add a tiebreaker such as `id`, or a page boundary can show one row twice and another never.
2. Large offsets are slow. `OFFSET 100000` still reads and discards 100,000 rows. For deep paging, use **keyset pagination**: remember the last key you showed and ask for `WHERE price < :last_price` (plus an id tiebreaker). The database can then seek straight to the right place using an index.

PostgreSQL also supports the SQL-standard spelling `FETCH FIRST 2 ROWS ONLY`. SQLite does not, but both understand `LIMIT`.

## The order a query is evaluated in

You write clauses in one order, but the database evaluates them, logically, in another:

```flow
FROM: pick the table(s)
WHERE: filter rows
GROUP BY: form groups (lesson 3)
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

`SELECT 7/2` returns `3`, not `3.5`, in both SQLite and PostgreSQL: dividing two integers gives an integer. Write `7/2.0` or `CAST(x AS REAL)` (PostgreSQL: `x::numeric`) when you want a fraction. `7 % 2` is the remainder, 1.

String concatenation uses `||`: `name || ' (' || city || ')'` gives `Asha (London)`. For Chloe it gives NULL, because anything combined with NULL is NULL. Lesson 4 is all about that.

## Key takeaways
- SQL is declarative: describe the rows you want, not how to find them.
- Use single quotes for strings; double quotes are for identifiers.
- `AND` binds tighter than `OR`. Bracket mixed conditions.
- Without `ORDER BY` there is no guaranteed order, and `LIMIT` without it returns arbitrary rows.
- Logical evaluation order is FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY, LIMIT. That is why `WHERE` can't see `SELECT` aliases in PostgreSQL.
- Prefer half-open date ranges (`>= start AND < next`) over `BETWEEN`.
- SQLite and PostgreSQL differ on `LIKE` case, NULL sort position and alias leniency. Test on the database you deploy.

## Further reading
- [SELECT — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-select.html)
- [Sorting rows (ORDER BY) — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-order.html)
- [Pattern matching (LIKE, ILIKE) — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-matching.html)
- [The SELECT statement — SQLite documentation](https://www.sqlite.org/lang_select.html)
- [Quirks, caveats and gotchas in SQLite](https://www.sqlite.org/quirks.html)
- [Paging through results without OFFSET — Use The Index, Luke](https://use-the-index-luke.com/no-offset)
