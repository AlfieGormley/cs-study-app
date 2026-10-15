---
id: sql-self-cross-joins
title: Join a table to itself and build combinations
level: basic
minutes: 4
sourceLesson: sql-joins
summary: Two aliases let one customer row match another as its referrer.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## Self joins

A table can be joined to itself. `customers.referred_by` points at another customer, so listing each customer with the name of whoever referred them needs two copies of the table with different aliases.

```sql
-- Use separate aliases for two customer
-- roles.
SELECT c.name, r.name AS referrer
FROM customers c
LEFT JOIN customers r
  ON r.id = c.referred_by;
```

| name | referrer |
|---|---|
| Asha | NULL |
| Ben | Asha |
| Chloe | Asha |
| Dev | Ben |
| Erin | NULL |

The aliases are what make it work: `c` is "the customer", `r` is "the referrer". With an inner join, Asha and Erin would disappear because nobody referred them.

Self joins also find pairs within a table. `ON a.city = b.city AND a.id < b.id` lists customers sharing a city (just Asha and Dev). The `a.id < b.id` stops each pair appearing twice and stops a row pairing with itself. Self joins handle one level of a hierarchy; walking a whole tree needs a recursive CTE.

## CROSS JOIN: every combination

```sql
-- Every customer pairs with every product.
SELECT COUNT(*)
FROM customers
CROSS JOIN products;
-- 25
```

A **cross join** (Cartesian product) pairs every row with every row, so its size is the product of the two tables' sizes:

```formula
n_cross = |A| × |B|
n_cross = 5 × 5 = 25
where
n_cross: the number of rows the cross join returns
A: the left table (here customers)
B: the right table (here products)
|A|: the number of rows in table A; vertical bars around a table name mean "how many rows it has", its cardinality
|B|: the number of rows in table B
In words: every row of A is paired once with every row of B, so the result has as many rows as the two row counts multiplied together.
```

The same product is the most an inner join can ever return: it keeps some of these pairs and drops the rest, so its row count can be zero or anything up to the cross join's count. A cross join is useful on purpose, for example to build a grid of every product for every store or date, which you then LEFT JOIN real sales onto so missing combinations show up as zero.

It is dangerous by accident. The old comma syntax `FROM customers c, orders o` is a cross join (5 × 6 = 30 rows here) until a `WHERE o.customer_id = c.id` turns it into an inner join. Forget the condition on two tables of a million rows each and you have asked for 1,000,000 × 1,000,000 = 1,000,000,000,000 rows: a trillion.

> [!note] SQLite versus PostgreSQL
> SQLite (and MySQL) accept `JOIN` with no `ON` and treat it as a cross join. PostgreSQL rejects it as a syntax error: an inner or outer join must have `ON`, `USING` or `NATURAL`. Only `CROSS JOIN` may omit a condition. SQLite also treats `CROSS JOIN` as an instruction not to reorder the two tables, which PostgreSQL does not.

## Key takeaways
- Two aliases let one customer row match another as its referrer.
- CROSS JOIN returns every left/right pair.
- Write CROSS JOIN explicitly when every combination is intended.

## Further reading
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [SELECT — SQLite docs](https://www.sqlite.org/lang_select.html)
