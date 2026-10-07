---
id: postgresql-in-practice
title: PostgreSQL in practice
level: intermediate
minutes: 25
summary: Build a small Postgres database, reason about concurrent writes, choose indexes and understand the maintenance and recovery work behind a reliable service.
---

PostgreSQL, usually called **Postgres**, is an open-source relational database server. SQL is the language you send it; Postgres is the system that stores rows, enforces constraints, coordinates concurrent sessions and recovers after a crash. It also supports JSON documents, extensible types and extensions, but those features do not remove the need to design your data carefully.

This lesson brings the pieces together around a small ticket shop. Read the SQL fundamentals first. The examples use PostgreSQL 18-compatible SQL; plans and timings depend on your data and installation. Run the examples in order in a fresh, disposable database, not an existing application database.

## 1. What runs where?

Your application uses a database driver to connect to the server. `psql` is another client: a terminal for sending SQL and inspecting the results. An ORM is another layer above a driver; it does not replace the database.

A PostgreSQL **cluster** means a collection of databases managed by a server installation. It does not necessarily mean several machines. A connection selects one database. Inside it, schemas such as `public` are namespaces containing tables, functions and other objects. `public.orders` names a table in a schema, not a different database.

Postgres normally uses a separate backend process for each client connection. Those processes share memory and coordinate access to storage. Connection pools reuse a bounded number of connections, avoiding a new backend for every web request. Increasing the connection limit is not a substitute for measuring CPU, memory, lock waits and throughput.

A typical request follows this path; responses travel back to the client:

```flow
Application sends parameterised SQL
Driver obtains a pooled connection
Postgres backend plans and executes
Result returns through the driver
Connection returns to the pool
```

With transaction pooling, the next transaction may use a different backend. Do not assume session settings or temporary objects will persist on the connection your application receives next.

To connect to a database that already exists locally:

```sh
psql -d postgres_study
```

Inside `psql`, `\conninfo` shows the connection, `\dt` lists tables and `\d events` describes a table. SQL statements end with a semicolon; these backslash commands are client commands. Use a non-superuser application role with only the required privileges, and bind user values through driver parameters rather than joining them into SQL strings.

## 2. Model the rules in the database

Create two tables. An event has available seats; a booking refers to an event and has an application-supplied request key.

```sql
CREATE TABLE events (
  id bigint GENERATED ALWAYS AS IDENTITY
    PRIMARY KEY,
  name text NOT NULL,
  seats_left integer NOT NULL
    CHECK (seats_left >= 0),
  starts_at timestamptz NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE bookings (
  id bigint GENERATED ALWAYS AS IDENTITY
    PRIMARY KEY,
  event_id bigint NOT NULL
    REFERENCES events(id),
  request_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL
    DEFAULT now()
);
```

The identity column generates values, while `PRIMARY KEY` enforces uniqueness. Generated IDs can have gaps, including after an aborted transaction; do not interpret the highest ID as the number of rows. A foreign key prevents a booking for a missing event. `CHECK` rejects negative availability, and `NOT NULL` separately rejects an unknown value: a check expression evaluating to NULL does not reject the row.

The unique request key will help identify retries of the same booking. Enforcing this in the database closes the race in which two requests both check for an existing key, find none, then insert duplicates.

Postgres automatically creates an index for a primary key or unique constraint. It does **not** automatically index the referencing side of every foreign key. Later, we will add an index starting with `bookings.event_id` to support lookups by event.

### Choose types for their meaning

| Value | Useful type | Reason |
|---|---|---|
| A count | `integer` | Exact whole number |
| A monetary amount | `numeric(12,2)` | Exact decimal arithmetic |
| An event instant | `timestamptz` | Represents a point in time |
| Optional attributes | `jsonb` | Queryable structured document |

`timestamptz` converts input to an instant and displays it in the session time zone. It does not preserve the original zone name. A recurring “9am Europe/London” schedule needs the named zone and scheduling rules as well as individual occurrence instants. For money, record the currency too; a decimal type cannot tell pounds from euros.

Insert the first event and inspect the generated ID:

```sql
INSERT INTO events
  (name, seats_left, starts_at, details)
VALUES (
  'Postgres workshop',
  2,
  '2027-05-01 10:00:00+00',
  '{"format":"online"}'
)
RETURNING id, seats_left;
```

In this fresh database the ID is 1. In an application, use the returned ID instead of assuming it. `RETURNING` avoids a separate query to discover which row was created.

## 3. Reserve a seat without overselling

An unsafe application reads `seats_left = 1`, checks it in application code and later writes `seats_left = 0`. Two clients can both read 1 and both claim success. Wrapping that read and write in a default transaction alone does not fix the race.

Instead, combine the condition and change in one statement:

```sql
UPDATE events
SET seats_left = seats_left - 1
WHERE id = 1 AND seats_left > 0
RETURNING id, seats_left;
```

A returned row means a seat was reserved. No returned row means no matching event with available seats. Under Read Committed, concurrent updates of this same row wait for each other; after the first commits, the second rechecks the condition against the updated row. Starting with one seat, only one update can succeed.

To reserve and record a booking atomically, use a transaction. This example is for a new request key and assumes the update returns one row:

```sql
BEGIN;

UPDATE events
SET seats_left = seats_left - 1
WHERE id = 1 AND seats_left > 0
RETURNING id;

INSERT INTO bookings
  (event_id, request_key)
VALUES (1, 'request-001')
RETURNING id;

COMMIT;
```

The application must inspect the update result. If it returns no rows, issue `ROLLBACK` and do not insert the booking. If the insert fails, roll back the transaction so the seat decrement is undone. An SQL error normally leaves the transaction aborted until rollback, unless you recover using a savepoint.

For a duplicate request key, roll back and then fetch the existing booking, checking that it belongs to the same intended request. Do **not** decrement a seat, use `ON CONFLICT DO NOTHING` for the booking and then commit regardless: the duplicate insert might do nothing while the extra decrement persists. A unique key is a building block for idempotency, not a complete workflow.

Keep transactions short. Do not hold the row lock while waiting for a customer or payment provider. External effects need their own retry and reconciliation design; rolling back SQL does not undo a payment API call.

## 4. MVCC, snapshots and isolation

Postgres uses **MVCC**: updates create new row versions, and snapshots decide which versions a query can see. Ordinary reads generally do not block ordinary writes, but writers updating the same row can block each other. Schema changes and explicit locks introduce other conflicts.

| Isolation | Read behaviour | Remaining responsibility |
|---|---|---|
| Read Committed | New snapshot per statement | Protect multi-step decisions |
| Repeatable Read | Stable transaction snapshot | Handle write skew and retries |
| Serializable | Successful work behaves serially | Retry aborted transactions |

Read Committed is the default. Two SELECTs in one transaction can see different committed values. Repeatable Read keeps a snapshot from its first non-transaction-control statement, but it is not full serial execution. At every level, a transaction can see its own prior writes.

Imagine two on-call staff, both active. Each transaction sees two active staff and marks a different person inactive. At Repeatable Read, they can update different rows and both commit, breaking the rule that someone must remain on call. This is **write skew**. Use a suitable shared locking protocol or Serializable transactions for all operations maintaining that rule.

Serializable can reject a conflicting transaction with SQLSTATE `40001`. Retry the **whole transaction**, including its reads and decisions, with a bounded retry policy. Retrying only the last statement can reuse a decision based on an obsolete snapshot. Deadlocks can also require a transaction retry; acquire multiple row locks in a consistent order to reduce them.

For a more involved read-then-change operation, `SELECT ... FOR UPDATE` can lock the selected rows. It does not lock an imaginary row that does not exist, so use constraints or a suitable isolation strategy for “insert if absent” rules.

## 5. Index for the query you actually run

Suppose an admin page needs an event's latest bookings:

```sql
CREATE INDEX bookings_event_recent
ON bookings (event_id, created_at DESC);

SELECT id, created_at
FROM bookings
WHERE event_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

This B-tree index puts the equality filter first and the requested ordering second. Postgres can find one event's entries in the desired order without sorting all its bookings. The index costs storage and maintenance on writes; adding one to every column is rarely a good trade.

Different index methods suit different operators:

- **B-tree** is the usual choice for equality, ranges and ordered retrieval.
- **GIN** supports inverted lookups, including many JSONB and full-text search operations.
- **BRIN** stores summaries over page ranges; it can be compact and useful when values correlate with physical order, such as append-heavy timestamp data. Candidate pages still need rechecking.

A sequential scan is not automatically bad: reading most rows, or a tiny table, can be cheaper than visiting an index and fetching heap rows. On this tiny example, do not expect the index to win.

Use the existing **Query Processing & Optimisation** lessons for deeper plan analysis. Start with this diagnostic on representative data:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, created_at
FROM bookings
WHERE event_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

`EXPLAIN` estimates a plan; `ANALYZE` here actually executes it. Costs are planner units, not milliseconds. Compare estimated versus actual row counts, inspect repeated loops, and look at buffer activity before changing settings. A shared-buffer read can still be served from the operating system cache, so it is not proof of a physical disk read. Do not add up inclusive timings of parents and children.

> [!warning] ANALYZE has two meanings
> `ANALYZE bookings` updates planner statistics. `EXPLAIN ANALYZE` runs the supplied query and measures execution, including writes if the query modifies data. Use a disposable database for write experiments; even rollback does not undo sequence increments or external side effects.

## 6. JSONB without abandoning a schema

Use relational columns for important keys, relationships and invariants. Use JSONB for attributes that genuinely vary, such as event presentation settings.

```sql
SELECT name
FROM events
WHERE details @> '{"format":"online"}';

CREATE INDEX events_details_gin
ON events USING gin (details);
```

The containment operator `@>` can use this GIN index for selective queries at sufficient scale. JSONB stores a processed representation rather than preserving input whitespace and key order. Duplicate object keys do not remain separate entries. Use `json` instead if preserving the input text matters more than JSONB's processing and indexing advantages.

A JSON document does not automatically enforce the types and relationships your application expects. If every event has a required capacity used in constraints and joins, a typed column is usually easier to validate and optimise than hiding it in JSON. Large document updates also carry write and index maintenance costs.

## 7. Vacuum and statistics are normal maintenance

Old row versions cannot be removed while a snapshot still needs them. **VACUUM** makes space from dead versions reusable and helps maintain visibility information and prevent transaction ID wraparound. Plain vacuum usually reuses space inside the table rather than returning all of it to the operating system.

**ANALYZE** samples data to update planner statistics. Postgres uses those estimates to choose scan and join strategies. Autovacuum automates vacuum and analyse work; monitor whether it keeps up rather than treating it as optional background noise.

In our disposable database you can run:

```sql
VACUUM (ANALYZE) bookings;
```

Run this outside a transaction block. A session left “idle in transaction” can retain locks and, when holding an old snapshot, prevent cleanup. If a busy table grows unexpectedly, inspect old transactions, dead tuples and autovacuum activity. Disabling autovacuum or routinely running `VACUUM FULL` is not a general fix: the latter rewrites the table and requires a strong lock.

## 8. WAL, replicas and recovery

**Write-ahead logging**, or WAL, records changes before corresponding data pages are written to durable storage. With normal durability settings, commit waits for the required WAL to be flushed; all changed table pages need not already be on disk. Recovery can replay logged changes after a crash. A checkpoint bounds recovery work; it is not a fresh backup.

This simplified local durability sequence assumes synchronous commit and normal storage settings:

```flow
Transaction changes buffered pages
WAL records describe the changes
Commit WAL is flushed durably
Server acknowledges the commit
```

Streaming replication sends WAL to a standby. Asynchronous replication can lag: a user may write on the primary and immediately read an older value on a standby. A failover can lose acknowledged transactions that never reached the promoted server. Synchronous replication can wait for a configured standby acknowledgement, trading latency and availability for stronger durability; whether replay is awaited depends on configuration.

Replication is not a backup. A mistaken DELETE can propagate to the standby. Protect recovery separately:

- A logical dump with `pg_dump` captures one database in a form that can be restored with PostgreSQL tools. Roles and other cluster-wide objects need separate handling.
- A physical base backup plus an unbroken archived WAL sequence supports **point-in-time recovery**, for example to just before an accidental deletion.
- Test restores into a separate environment and measure recovery time. A successful backup command alone does not prove you can recover.

Choose a recovery point objective (acceptable lost work) and recovery time objective (acceptable downtime). Those requirements determine backup frequency, WAL retention, replica configuration and the restore procedure. A managed provider automates some of this, but you still need to understand its retention and recovery guarantees.

## 9. A practical troubleshooting order

When a request is slow, first separate time waiting for a connection, waiting for a lock, executing SQL and transferring results. `pg_stat_activity` exposes current sessions and waits; `pg_locks` helps investigate blocking. The optional `pg_stat_statements` extension aggregates query behaviour over time when configured.

Next, reproduce the query with representative parameters, examine its plan and check statistics. Then consider query shape, indexes, transaction duration and pool size. Avoid tuning memory or connection limits blindly: a per-operation memory allowance can multiply across operations and concurrent sessions.

For a slow event booking, a lock wait on one popular event may dominate even when the primary-key lookup is fast. Another index cannot remove the need for competing reservations to coordinate over the same remaining seat count.

## Key takeaways

- Postgres is a database server; SQL, drivers, pools and ORMs occupy different parts of the stack.
- Put invariants in constraints, choose meaningful types and inspect the result of conditional writes.
- MVCC reduces read/write interference but does not make every concurrent workflow correct. Isolation, locks and whole-transaction retries still matter.
- Choose indexes for measured query patterns. JSONB complements relational modelling; it does not replace constraints.
- Vacuum, statistics, WAL, replication and tested backups solve different problems. A replica alone cannot undo a mistaken write.

## Further reading

- [Client/server architecture — PostgreSQL](https://www.postgresql.org/docs/current/tutorial-arch.html)
- [Constraints — PostgreSQL](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [Date and time types — PostgreSQL](https://www.postgresql.org/docs/current/datatype-datetime.html)
- [Transaction isolation — PostgreSQL](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Using EXPLAIN — PostgreSQL](https://www.postgresql.org/docs/current/using-explain.html)
- [Index types — PostgreSQL](https://www.postgresql.org/docs/current/indexes-types.html)
- [JSON types — PostgreSQL](https://www.postgresql.org/docs/current/datatype-json.html)
- [Routine vacuuming — PostgreSQL](https://www.postgresql.org/docs/current/routine-vacuuming.html)
- [Write-ahead logging — PostgreSQL](https://www.postgresql.org/docs/current/wal-intro.html)
- [Standby servers and replication — PostgreSQL](https://www.postgresql.org/docs/current/warm-standby.html)
- [Backup and restore — PostgreSQL](https://www.postgresql.org/docs/current/backup.html)
