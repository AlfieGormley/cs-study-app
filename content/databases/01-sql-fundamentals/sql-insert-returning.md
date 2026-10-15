---
id: sql-insert-returning
title: Insert named columns and read generated values
level: intermediate
minutes: 3
sourceLesson: sql-dml-constraints
summary: Name INSERT columns so a schema change cannot shift the values.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. Examples of writes start from that original data unless a block explicitly groups statements together.

Reading data can only give you a wrong answer. Writing data can destroy it. This lesson covers the three statements that change rows, known together as **DML** (data manipulation language): `INSERT`, `UPDATE` and `DELETE`. It also covers the **constraints** that make the database refuse changes that would break your rules.

The examples use the module's shop schema. Each one starts from the original data.

## INSERT

Always name the columns you are filling:

```sql
-- Omitted ids and referrals use their
-- defaults.
INSERT INTO customers (name, city)
VALUES ('Femi', 'Leeds');
```

Columns you leave out get their **default**, which is NULL unless the table says otherwise. Here `referred_by` is NULL. `id` is an `INTEGER PRIMARY KEY`, so SQLite assigns the next number, 6. (PostgreSQL uses an identity column or sequence for the same job; see the next lesson.)

`INSERT INTO customers VALUES (...)` without a column list also works, but it depends on the column order in the table. Add a column later and every such statement breaks, or worse, puts values in the wrong columns.

### Several rows, and RETURNING

One statement can insert many rows. This usually reduces parsing and round-trip work compared with many single-row statements. In autocommit mode it also avoids a separate commit for each row; inside an explicit transaction those statements already share a commit:

```sql
-- Return the generated keys with the names.
INSERT INTO products (name, price)
VALUES ('Jug', 12), ('Tray', 15)
RETURNING id, name;
```

| id | name |
|---|---|
| 6 | Jug |
| 7 | Tray |

`RETURNING` hands back the rows as they were written, including generated ids and defaults, without a second query. PostgreSQL has had it for a long time; SQLite added it in 3.35.

### INSERT ... SELECT

The rows can come from a query instead of `VALUES`:

```sql
-- Copy two home products into larger
-- variants.
INSERT INTO products
  (name, price, category)
SELECT name || ' XL', price * 2,
       category
FROM products
WHERE category = 'home';
```

This adds "Lamp XL" at £80 and "Rug XL" at £180. The copy happens inside the database, so no data travels to your application and back.

If a row might already exist, `INSERT ... ON CONFLICT` (an **upsert**) can update it instead. Module 2 covers upserts properly.

## Key takeaways
- Name INSERT columns so a schema change cannot shift the values.
- Omitted columns use defaults, including generated ids.
- Multi-row INSERT and RETURNING can reduce database round trips.

## Further reading
- [Data manipulation — PostgreSQL documentation](https://www.postgresql.org/docs/current/dml.html)
