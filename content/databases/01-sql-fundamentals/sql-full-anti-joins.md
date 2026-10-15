---
id: sql-full-anti-joins
title: Keep both sides or find missing matches
level: basic
minutes: 4
sourceLesson: sql-joins
summary: RIGHT JOIN preserves the right side; FULL JOIN preserves both sides.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## RIGHT and FULL OUTER JOIN

A **RIGHT JOIN** is the mirror image: keep every row of the right table.

```sql
-- Keep guest order 106 from the right side.
SELECT c.name, o.id
FROM customers c
RIGHT JOIN orders o
  ON o.customer_id = c.id;
```

This returns the five matched rows plus `NULL | 106`: the guest order is kept, Erin is not. Any right join can be rewritten as a left join by swapping the tables, and most teams do exactly that so queries read consistently left to right.

A **FULL OUTER JOIN** keeps unmatched rows from both sides.

```sql
-- Keep both Erin and the guest order.
SELECT c.name, o.id
FROM customers c
FULL JOIN orders o
  ON o.customer_id = c.id;
```

| name | id |
|---|---|
| Asha | 101 |
| Asha | 102 |
| Ben | 103 |
| Chloe | 104 |
| Dev | 105 |
| Erin | NULL |
| NULL | 106 |

A full join adds the unmatched rows of both sides to the matching pairs:

```formula
n_full = m + u_L + u_R
n_full = 5 + 1 + 1 = 7
where
n_full: the number of rows the FULL OUTER JOIN returns
m: the number of matching pairs, the inner join's row count (5)
u_L: left-table rows with no match, padded on the right with NULLs (1, Erin)
u_R: right-table rows with no match, padded on the left with NULLs (1, order 106)
In words: a full join is the inner join plus every leftover row from either side, each shown once with NULLs where its partner would be.
```

Full joins are rarer. They suit reconciliation jobs: "compare yesterday's export with today's and show rows missing from either side".

> [!warning] Engine support
> PostgreSQL supports RIGHT and FULL joins. SQLite only added them in version 3.39 (2022), so older SQLite builds reject them. MySQL still has no FULL OUTER JOIN; a duplicate-preserving emulation uses a LEFT JOIN plus `UNION ALL` of only the unmatched right-side rows. A plain `UNION` removes duplicate output rows.

## The anti-join: rows with no match

"Which customers have never ordered?" is a LEFT JOIN followed by a test for the NULLs it creates.

```sql
-- A NULL order key identifies no match.
SELECT c.name
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
WHERE o.id IS NULL;
```

The result is just `Erin`. The same pattern finds products nobody has bought (`Rug`).

Test a column that can never be NULL in a real match, such as the right table's primary key. If you tested a nullable column like `o.status`, a genuine match with a NULL status would be misreported as "no match". `NOT EXISTS` expresses the same idea and is often clearer; subqueries come in the next module. Avoid `NOT IN` against a nullable column; the NULL units show why it can silently return nothing.

## Key takeaways
- RIGHT JOIN preserves the right side; FULL JOIN preserves both sides.
- A FULL JOIN adds unmatched rows to the matching pairs.
- Find missing matches by testing a non-nullable right-hand key after LEFT JOIN.

## Further reading
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [SQLite 3.39.0 release notes (RIGHT and FULL JOIN)](https://sqlite.org/releaselog/3_39_0.html)
- [Join (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Join_(SQL))
