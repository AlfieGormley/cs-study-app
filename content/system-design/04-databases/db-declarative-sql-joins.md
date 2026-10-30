---
id: db-declarative-sql-joins
title: Declarative SQL and join costs
level: basic
minutes: 4
summary: Read a query plan, choose a join shape, and avoid LEFT JOIN filtering errors and N+1 round trips.
sourceLesson: db-relational-acid
---

SQL separates the result you ask for from the access path that produces it. Use that separation to fetch related data in one deliberate query rather than many network trips.

## SQL is declarative

You describe *what* you want; the **query planner** decides *how* to get it: which index to use, which join algorithm, which order to join tables in. This is a big deal. The same query can go from a full scan to an index lookup after you add an index, with no application change.

```sql
-- Aggregate paid orders for each user.
SELECT u.email, sum(o.total_p) AS spent
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.status = 'paid'
GROUP BY u.email
ORDER BY spent DESC
LIMIT 10;
```

The SQL fragments assume the tables and suitable rows already exist; results depend on those rows. The query above returns at most ten users, ranked by paid spend in pence.

Run `EXPLAIN` in front of a query to see the plan the database chose, or `EXPLAIN ANALYZE` to also run it and report how long each step actually took. Because `ANALYZE` really executes the statement, wrap an `UPDATE` or `DELETE` in a transaction you roll back.

## Joins

A join combines rows from two tables on a condition.

| Join | Returns |
|---|---|
| `INNER` | Only rows matching on both sides |
| `LEFT` | All left rows, NULLs if no match |
| `FULL` | All rows from both sides |
| `CROSS` | Every combination (rarely wanted) |

Under the hood the planner picks one of three algorithms:

- **Nested loop**: for each outer row, look up matches in the inner table. Great when the outer side is small and the inner side has an index.
- **Hash join**: build a hash table on the smaller input, then stream the larger one past it. Good for large, unsorted inputs with equality conditions.
- **Merge join**: sort both sides on the join key (or read them in index order) and walk them together.

> [!warning] A WHERE clause can undo a LEFT JOIN
> `users u LEFT JOIN orders o ON o.user_id = u.id WHERE o.status = 'paid'` silently drops users with no orders: their `o.status` is NULL, and the `WHERE` filters NULL out. To keep them, put the condition in the join: `ON o.user_id = u.id AND o.status = 'paid'`.

> [!warning] The N+1 query problem
> An ORM loop that loads 100 orders and then runs one query per order to fetch its user makes 101 round trips. At 1 ms each that is about a tenth of a second spent waiting on the network before any query does real work.

The name comes from the count: one query for the list, plus one more for every row in it. Each query waits for a full network round trip, so the waiting grows in step with the length of the list even when every individual query is fast. That is why the problem hides in development, where the database sits on the same machine, and appears in production, where every trip crosses a network.

A join removes the per-row queries entirely; batching (one `WHERE id IN (...)` query for all the users) leaves two. Some ORMs batch or prefetch associations for you and some load them lazily, one at a time, so check the queries yours actually sends: most can log them.

> [!analogy] Real-world analogy: one shopping trip per ingredient
> Imagine cooking from a recipe by driving to the shop, buying one ingredient, driving home, reading the next line, and driving back again. Each trip is quick, but twenty ingredients means twenty journeys. Taking the whole list on one trip is far faster even though the shopping itself takes as long.
>
> **How it maps:** Each drive is a network round trip to the database, each ingredient is one row's lookup, and the shopping list is a join or a batched `IN` query that fetches everything in one request.
>
> **Where it stops:** The database still has to do the work for every row in a batched query, so a huge batch is not free. Sending the per-row queries concurrently shortens the wait but still multiplies the number of queries the database must handle.

## Key takeaways
- The planner chooses indexes and join algorithms from the query and data.
- Move a right-side filter into ON when a LEFT JOIN must retain unmatched left rows.
- N+1 loading pays one round trip per row; joins or batching collapse them into one or two requests.

## Further reading
- [PostgreSQL: Joins Between Tables](https://www.postgresql.org/docs/current/tutorial-join.html)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
