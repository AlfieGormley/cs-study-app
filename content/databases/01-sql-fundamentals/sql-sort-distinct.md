---
id: sql-sort-distinct
title: Sort rows and remove duplicate results
level: basic
minutes: 3
sourceLesson: sql-select-basics
summary: ORDER BY is necessary for a guaranteed result order.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## ORDER BY: sorting

**Without `ORDER BY`, row order is not guaranteed.** It often looks stable on a small table, then changes after a database index is added, the table grows or the planner picks a parallel plan. If order matters, say so.

```sql
-- Sort each category by decreasing price.
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

## Key takeaways
- ORDER BY is necessary for a guaranteed result order.
- Each sort direction applies only to its own column.
- DISTINCT removes duplicate whole rows and retains one NULL.

## Further reading
- [Sorting rows (ORDER BY) — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-order.html)
- [The SELECT statement — SQLite documentation](https://www.sqlite.org/lang_select.html)
