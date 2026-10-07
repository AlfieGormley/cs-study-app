---
id: db-relational-acid
title: Relational databases and ACID
level: basic
minutes: 11
summary: Tables, schemas, keys and joins, what ACID actually promises, and when to normalise or denormalise.
---

Relational databases are a common choice for transactional data: PostgreSQL, MySQL, SQL Server, Oracle, or a cloud variant such as Amazon Aurora. Before reaching for anything more exotic, you need to know what the relational model gives you for free.

## The relational model

A relational database stores data in **tables** (relations). Each table has a fixed set of typed **columns**, and each **row** is one record.

- A **primary key** uniquely identifies each row (`users.id`).
- A **foreign key** is one or more columns referring to an eligible unique or primary key, possibly in the same table (`orders.user_id → users.id`). The database can enforce that the referenced row exists.
- **Constraints** (`NOT NULL`, `UNIQUE`, `CHECK`) push data rules into the database so that every application that writes to it obeys them.

```sql
CREATE TABLE users (
  id         bigserial PRIMARY KEY,
  email      text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL
             DEFAULT now()
);

CREATE TABLE orders (
  id       bigserial PRIMARY KEY,
  user_id  bigint NOT NULL
           REFERENCES users(id),
  total_p  integer NOT NULL
           CHECK (total_p >= 0),
  status   text NOT NULL
);
```

The **schema** is the set of table definitions. Relational databases are *schema-on-write*: data that doesn't fit the schema is rejected when you write it. Document stores often permit flexible document shapes, but many also enforce declared validation rules; readers must handle permitted historical shapes.

> [!tip] Store money as integers
> `total_p` stores pence. Floating-point types can't represent 0.10 exactly, so sums drift. Use integer minor units or `numeric`.

## SQL is declarative

You describe *what* you want; the **query planner** decides *how* to get it: which index to use, which join algorithm, which order to join tables in. This is a big deal. The same query can go from a full scan to an index lookup after you add an index, with no application change.

```sql
SELECT u.email, sum(o.total_p) AS spent
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.status = 'paid'
GROUP BY u.email
ORDER BY spent DESC
LIMIT 10;
```

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

## ACID

A **transaction** groups several reads and writes into one logical unit. ACID describes what the database promises about it.

- **Atomicity**: all of the transaction's writes happen, or none do. If the server crashes halfway through, the partial work is rolled back. "Abortability" would be a better name.
- **Consistency**: the transaction takes the database from one valid state to another, according to your invariants (constraints, foreign keys). This is mostly the *application's* responsibility; the database only enforces the constraints you declared.
- **Isolation**: concurrent transactions don't see each other's half-finished work. How strong this is depends on the *isolation level*, which is a whole lesson later in this module.
- **Durability**: with a durable commit configuration and functioning storage, an acknowledged commit survives the failures covered by that configuration. In practice this means it has been flushed to a write-ahead log on disk (and possibly to replicas).

```sql
BEGIN;
UPDATE accounts SET balance = balance - 5000
  WHERE id = 1;
UPDATE accounts SET balance = balance + 5000
  WHERE id = 2;
COMMIT;
```

If the process dies after the first `UPDATE`, atomicity guarantees that the debit is undone. No money vanishes.

> [!note] The C in ACID isn't the C in CAP
> ACID consistency means "invariants hold". CAP consistency means linearizability across replicas. Same word, unrelated ideas. Consistency models get their own module.

## Normalisation

**Normalisation** means structuring tables so that each fact is stored in exactly one place. The goal is to avoid *update anomalies*: if a customer's address is copied into every order row, changing it means updating hundreds of rows, and missing one leaves the data contradicting itself.

The normal forms, informally:

1. **1NF**: each column holds one atomic value; no repeating groups like `phone1, phone2, phone3`.
2. **2NF**: each non-prime attribute depends on the whole of every candidate key, not a proper subset of a composite candidate key.
3. **3NF**: non-key columns depend only on the key, not on other non-key columns. ("The key, the whole key, and nothing but the key.") For example, `employees(id, dept_id, dept_name)` breaks 3NF: `dept_name` depends on `dept_id`, which depends on `id`.

```
Denormalised order_lines:
 order_id | product_id | product_name | qty
 ---------+------------+--------------+----
 1        | 7          | Kettle       | 1
 2        | 7          | Kettle       | 2

product_name depends on product_id, not on
the key (order_id, product_id): 2NF broken.
Rename the product and you must edit every
line. Fix: move name into products(id,name).
```

## Denormalisation

Normalised data needs joins to reassemble. At large scale, or when one read path dominates, you may deliberately **denormalise**: duplicate data so that reads are cheaper.

| | Normalised | Denormalised |
|---|---|---|
| Writes | One place to update | Many copies to keep in sync |
| Reads | Joins needed | Single lookup |
| Storage | Smaller | Larger |
| Risk | Slow joins | Inconsistent copies |

Common, sensible denormalisations:

- A `comment_count` column on `posts`, updated in the same transaction as the insert into `comments`.
- Copying the price into `order_lines` at purchase time. This one is actually *correct* modelling: the historical price is a different fact from the current price.
- Materialised views or read models built from the normalised source of truth.

> [!example] Rule of thumb
> Start normalised. Denormalise a specific read path when you've measured that it's too slow, and decide up front how the copies will be kept in sync (same transaction, trigger, or an async pipeline that tolerates lag).

## Why relational databases scale further than people think

Single-node capacity depends on transaction shape, indexes, contention, hardware and recovery objectives. Measure these before introducing distribution. Universal throughput figures and company deployment anecdotes are absent because no matching benchmark or dated primary incident source is established here. The usual reasons to move beyond a single relational primary are write throughput beyond one machine, data volume beyond one machine, or very specific access patterns, all of which later lessons cover.

## Key takeaways
- Relational databases give you schemas, constraints, declarative SQL and joins; the planner chooses how to execute queries.
- ACID: atomicity (all or nothing), consistency (your invariants hold), isolation (concurrent transactions don't interfere, to a degree set by the isolation level), durability (committed means it survives a crash).
- Normalise so each fact lives in one place; denormalise specific hot read paths deliberately and plan how copies stay in sync.
- Watch for N+1 queries; one join beats a hundred round trips.
- A single well-tuned relational server goes a very long way before you need to distribute it.

## Further reading
- [PostgreSQL: Joins Between Tables](https://www.postgresql.org/docs/current/tutorial-join.html)
- [PostgreSQL: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [Wikipedia: ACID](https://en.wikipedia.org/wiki/ACID)
- [Wikipedia: Database normalization](https://en.wikipedia.org/wiki/Database_normalization)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
