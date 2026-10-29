---
id: sql-shop-select
title: Read the shop tables and choose columns
level: basic
minutes: 5
sourceLesson: sql-select-basics
summary: Use the shop keys to identify customers, products, orders and their lines.
---

SQL queries are **declarative**: you describe the rows you want and the database works out how to fetch them. A SELECT does not require a loop in your application. That is why one short query can replace much procedural code, and also why small slips in a query can quietly give you the wrong answer.

> [!analogy] Real-world analogy: ordering from a menu
> In a restaurant you say what you want to eat, not which pan to heat or which shelf to open. The kitchen decides how to prepare it.
>
> **How it maps:** A SELECT is the order: it states which rows and columns you want. The database's query planner is the kitchen, choosing indexes, join methods and the order of work.
>
> **Where it stops:** A kitchen may interpret a vague order generously, but the database returns exactly the rows your query describes, mistakes included. It also promises no particular row order unless you ask for one with ORDER BY.

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

`order_items` links orders to products with a quantity. Here is the complete fixture; the pair of order and product ids identifies each line.

| order_id | product_id | qty |
|---|---|---|
| 101 | 1 | 1 |
| 101 | 5 | 4 |
| 102 | 3 | 2 |
| 103 | 2 | 1 |
| 103 | 5 | 2 |
| 104 | 1 | 1 |
| 104 | 3 | 1 |
| 105 | 2 | 1 |
| 106 | 5 | 1 |

Prices are whole pounds to keep the arithmetic easy. Order 106 is a guest checkout with no customer, Erin has never ordered, and nobody has bought the Rug. Those gaps matter in later lessons. The original fixture uses integer primary keys, required names and prices, and enforced foreign keys from orders and lines; the final units show a redesigned schema.

Result tables illustrate the expected SQLite behaviour of the small shop examples. Differences from PostgreSQL are called out.

Unless ORDER BY specifies otherwise, a displayed result table shows the returned rows in a convenient illustrative order. SQLite and PostgreSQL can emit those same rows in a different order. An ordinary equality comparison with a NULL city is unknown, so WHERE does not keep it; this matters for the quoting question at the end of this unit.

## SELECT and FROM

The smallest useful query names some columns and a table:

```sql
-- Read only the two needed product fields.
SELECT name, price
FROM products;
```

`SELECT *` returns every column. It is handy at the prompt but a bad habit in application code: adding a column to the table silently changes what your code receives, and you pull more data than you need.

You can compute new columns and name them with `AS`:

```sql
-- Compute a value without changing prices.
SELECT name, price * 2 AS double_price
FROM products;
```

The name after `AS` is an **alias**. Strings use **single quotes**: `'London'`. Double quotes are for identifiers, such as a column called `"order"` that clashes with a keyword.

> [!warning] Double quotes in SQLite
> When legacy double-quoted-string compatibility is enabled, SQLite has a quirk: if `"London"` is not a column name, it treats it as the string `'London'`. PostgreSQL raises `column "London" does not exist`. Worse, `WHERE city = "city"` in SQLite compares the column with itself. Always use single quotes for strings.

## Key takeaways
- Use the shop keys to identify customers, products, orders and their lines.
- SELECT chooses output columns; AS names a computed column.
- Single quotes mean text; double quotes name identifiers.

## Further reading
- [SELECT — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-select.html)
- [The SELECT statement — SQLite documentation](https://www.sqlite.org/lang_select.html)
- [Quirks, caveats and gotchas in SQLite](https://www.sqlite.org/quirks.html)
