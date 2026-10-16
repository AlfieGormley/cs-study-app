---
id: asql-outer-join-filters
title: Filtering optional matches without losing customers
level: advanced
minutes: 3
summary: An ON filter limits matches while retaining the outer customer.
sourceLesson: asql-interview-problems
---

The shop customers are Ana, Ben, Cat, Dev and Eve. Ana ordered 120, 60 and 60; Ben 45 and 90; Cat 200 and 30; Dev 45; Eve none. orders.id is a non-NULL primary key.

## 8. The LEFT JOIN filter trap

"List every customer with their orders over 100." Where the filter goes changes the answer:

```sql
-- Limit matches but retain customers.
-- Filter in ON: keeps all customers
SELECT c.name, o.total
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
 AND o.total > 100;
```

This returns all five customers: Ana 120, Cat 200, and NULLs for Ben, Dev and Eve. Move `o.total > 100` to WHERE and the join first includes every real order plus Eve's padded row. WHERE rejects Ben and Dev's small orders and Eve's NULL, leaving Ana and Cat. This NULL-rejecting predicate makes the result equivalent to an inner join; other WHERE predicates can preserve padded rows.

For counts, keep the same ON condition but select COUNT(o.id) and group by the customer key. Ana has one qualifying order over 100, Cat one, and Ben, Dev and Eve zero. COUNT(*) would count every padded row and incorrectly give those three customers one.

The predicate’s purpose determines placement. A condition restricting which optional orders qualify belongs in ON when every customer must survive. A condition deciding which customers belong in the report can still go in WHERE. For example, a filter on the customer’s city deliberately removes other customers. Moving predicates mechanically between clauses can therefore change the business question.

## Key takeaways
- An ON filter limits matches while retaining the outer customer.
- COUNT(o.id) counts actual orders and ignores the padded NULL row.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
