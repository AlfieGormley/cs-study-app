---
id: sql-filter-precedence
title: Filter products with deliberate brackets
level: basic
minutes: 3
sourceLesson: sql-select-basics
summary: WHERE keeps only true conditions.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## WHERE: filtering rows

`WHERE` keeps only the rows for which a condition is true.

```sql
-- Keep the expensive products, largest
-- first.
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
-- Kitchen rows bypass the price test here.
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
-- WHERE fragment after SELECT from
-- products.
WHERE (category = 'kitchen'
       OR category = 'home')
  AND price > 50;
```

Now only Rug is returned. When a condition mixes `AND` and `OR`, always add brackets, even when you know the precedence. The next reader may not.

## Key takeaways
- WHERE keeps only true conditions.
- BETWEEN includes both bounds; LIKE uses % and _ as wildcards.
- Bracket mixed AND and OR conditions to state the intended groups.

## Further reading
- [SELECT — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-select.html)
- [Pattern matching (LIKE, ILIKE) — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-matching.html)
- [The SELECT statement — SQLite documentation](https://www.sqlite.org/lang_select.html)
