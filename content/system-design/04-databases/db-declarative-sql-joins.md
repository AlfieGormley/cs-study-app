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
> An ORM loop that loads 100 orders and then runs one query per order to fetch its user makes 101 round trips. At 1 ms each that is 101 ms of round-trip latency before execution. A join can make one trip; fetching orders then users in bulk usually makes two.

The name comes from the count: one query for the list, plus one more for each of the N rows in it. Because every query waits for a full network round trip, the time grows with the length of the list even when each query is fast:

```formula
Q = 1 + N
T = Q × t_RTT
where
Q: the total number of queries sent to the database
N: the number of rows in the first result (here, orders), each of which triggers one extra query
T: the total time spent waiting on round trips, in milliseconds (ms), before any query execution time
t_RTT: the round-trip time of one query between the application and the database, in milliseconds (ms); it depends on network distance, and the example below assumes 1 ms
ms: millisecond, one thousandth of a second
In words: every extra row in the list costs one more round trip, so the waiting time grows in step with the length of the list.
```

For the 100 orders above at 1 ms per round trip:

```formula
Q = 1 + 100 = 101
T = 101 × 1 ms = 101 ms
where
Q: the total number of queries
T: the total round-trip waiting time, in milliseconds (ms)
ms: millisecond, one thousandth of a second
In words: 101 queries at 1 ms each spend about a tenth of a second just waiting on the network.
```

A join replaces the N extra queries with none, so Q falls to 1. The formula assumes the queries run one after another; an ORM that batches or runs them in parallel changes the count, which is why you should check what your ORM actually sends.

## Key takeaways
- The planner chooses indexes and join algorithms from the query and data.
- Move a right-side filter into ON when a LEFT JOIN must retain unmatched left rows.
- N+1 loading makes one list query plus one query per row; joins or batching reduce round trips.

## Further reading
- [PostgreSQL: Joins Between Tables](https://www.postgresql.org/docs/current/tutorial-join.html)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
