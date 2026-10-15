---
id: sql-update-old-values
title: Update rows using their previous values
level: intermediate
minutes: 3
sourceLesson: sql-dml-constraints
summary: UPDATE expressions read the previous row values.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. Examples of writes start from that original data unless a block explicitly groups statements together.

## UPDATE

`UPDATE` changes columns in every row that matches `WHERE`:

```sql
-- Raise only the two kitchen product
-- prices.
UPDATE products
SET price = price + 5
WHERE category = 'kitchen'
RETURNING name, price;
```

| name | price |
|---|---|
| Kettle | 35 |
| Toaster | 30 |

The right-hand side of `SET` sees the **old** row values. `SET a = b, b = a` swaps two columns in standard SQL and in PostgreSQL and SQLite, because both expressions read the values from before the update.

`WHERE` can use a subquery:

```sql
-- Compare with the pre-update mean price.
UPDATE products SET price = price * 2
WHERE price > (SELECT AVG(price)
               FROM products);
```

The subquery's average is the ordinary mean of the five prices:

```formula
mean = (x_1 + x_2 + … + x_n) / n
mean = (30 + 25 + 40 + 90 + 8) / 5
mean = 193 / 5 = £38.6
where
mean: the arithmetic mean, which is what AVG(price) returns, in pounds (£)
x_1, x_2, x_n: the prices being averaged, in pounds (£)
…: "and so on": every price between x_2 and x_n is included too
n: how many prices there are (5); AVG leaves NULLs out of both the sum and n
In words: the average is the total of the prices divided by how many there are.
```

This uncorrelated average subquery has no reference to the outer product row. SQLite evaluates it once and reuses its result; PostgreSQL evaluates it against the statement's snapshot. Only Lamp (£40) and Rug (£90) exceed £38.6 and get doubled. The threshold stays fixed for this query. Do not generalise that to a correlated subquery reading the table being changed: SQLite can see changes made earlier by the same statement.

To update using another table, PostgreSQL and SQLite (3.33+) both support `UPDATE ... FROM`. Mark every London customer's orders:

```sql
-- Mark orders belonging to London
-- customers.
UPDATE orders SET status = 'vip'
FROM customers c
WHERE c.id = orders.customer_id
  AND c.city = 'London';
```

That updates 101, 102 and 105. MySQL spells this differently (`UPDATE orders JOIN customers ...`), so this is one place where portable SQL is hard.

## Key takeaways
- UPDATE expressions read the previous row values.
- A scalar average subquery here uses the pre-statement data.
- An UPDATE matching no rows succeeds with an affected count of zero.

## Further reading
- [Data manipulation — PostgreSQL documentation](https://www.postgresql.org/docs/current/dml.html)
- [The UPDATE statement — SQLite documentation](https://www.sqlite.org/lang_update.html)
