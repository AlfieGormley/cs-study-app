---
id: sql-outer-predicates
title: Place outer join predicates deliberately
level: basic
minutes: 3
sourceLesson: sql-joins
summary: ON decides which pairs match before outer padding.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## ON versus WHERE in an outer join

This is the classic outer join bug. Say you want every customer, plus their *shipped* orders. Where does the `status` filter go?

```sql
-- Match shipped orders; keep every
-- customer.
-- Filter in ON
SELECT c.name, o.id, o.status
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
 AND o.status = 'shipped';
```

| name | id | status |
|---|---|---|
| Asha | 101 | shipped |
| Asha | 102 | shipped |
| Ben | NULL | NULL |
| Chloe | 104 | shipped |
| Dev | NULL | NULL |
| Erin | NULL | NULL |

```sql
-- Remove rows without a shipped order.
-- Filter in WHERE
SELECT c.name, o.id, o.status
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
WHERE o.status = 'shipped';
```

| name | id | status |
|---|---|---|
| Asha | 101 | shipped |
| Asha | 102 | shipped |
| Chloe | 104 | shipped |

Why the difference? The logical order is: build the join (using `ON`), *then* apply `WHERE`.

- In `ON`, the filter decides which right rows count as a **match**. Ben's only order is pending, so he has no match and is padded with NULLs, but he is kept.
- In `WHERE`, the filter runs **after** the padding. Ben has status `pending`, Dev has `cancelled`, and only Erin is NULL-padded. None satisfies `status = 'shipped'`, so all three are removed. The LEFT JOIN has quietly become an INNER JOIN.

> [!analogy] Real-world analogy: a class register of handed-in homework
> A teacher prints a register listing every pupil, with the homework each handed in, leaving a blank where nothing arrived. Before printing, the teacher can decide that late homework does not count. After printing, the teacher can also cross out lines.
>
> **How it maps:** The LEFT JOIN is the register: every customer gets a line, blank (NULL) if nothing matched. A condition in `ON` is the rule about which homework counts: a pupil whose only homework was late still gets a line, just with a blank. A condition in `WHERE` is crossing out finished lines: "cross out every line without on-time homework" also removes the pupils with blanks.
>
> **Where it stops:** On paper a blank plainly means "nothing handed in". In SQL the blank is NULL, so a test on it is UNKNOWN rather than FALSE, and `WHERE` drops UNKNOWN rows too. Even a test that sounds as if it should keep blanks, such as `o.status <> 'pending'`, removes every padded row unless you add `OR o.id IS NULL`.

The rule of thumb:

- Conditions on the **optional** (right) table go in `ON` if you want to keep unmatched left rows.
- Conditions that should remove **left** rows go in `WHERE`.

The reverse surprise exists too. Putting `AND c.city = 'London'` in the `ON` of a LEFT JOIN does *not* remove Ben, Chloe or Erin. It just stops them matching any order, so they come back padded with NULLs. To keep only London customers, that test belongs in `WHERE`. For an INNER JOIN, `ON` and `WHERE` filters give the same result.

## Key takeaways
- ON decides which pairs match before outer padding.
- A NULL-rejecting WHERE predicate removes padded rows.
- A predicate on the left table belongs in WHERE when it should remove left rows.

## Further reading
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [SELECT — SQLite docs](https://www.sqlite.org/lang_select.html)
