---
id: db-acid-transfer-guarantees
title: ACID and an atomic transfer
level: basic
minutes: 3
summary: Trace a two-account transfer and separate database guarantees from application invariants and external effects.
sourceLesson: db-relational-acid
---

A transfer changes two balances but represents one business event. Transactions let the database commit those row changes together; the application must still define which business rules make the transfer valid.

## ACID

A **transaction** groups several reads and writes into one logical unit. ACID describes what the database promises about it.

- **Atomicity**: all of the transaction's writes happen, or none do. If the server crashes halfway through, the partial work is rolled back. "Abortability" would be a better name.
- **ACID consistency**: the transaction takes the database from one valid state to another, according to your invariants (constraints, foreign keys). This is mostly the *application's* responsibility; the database only enforces the constraints you declared.
- **Transaction isolation**: concurrent transactions don't see each other's half-finished work. How strong this is depends on the *isolation level*, which is a whole lesson later in this module.
- **Durability**: with a durable commit configuration and functioning storage, an acknowledged commit survives the failures covered by that configuration. In practice this means it has been flushed to a write-ahead log on disk (and possibly to replicas).

```sql
-- Both account rows must already exist.
BEGIN;
-- Move 5,000 minor units as one
-- transaction.
UPDATE accounts SET balance = balance - 5000
  WHERE id = 1;
UPDATE accounts SET balance = balance + 5000
  WHERE id = 2;
-- Make both balance changes visible.
COMMIT;
```

The SQL assumes an `accounts(id, balance)` table with both rows present and a business decision that permits the transfer. Neither UPDATE by itself proves those prerequisites.

If the process dies after the first `UPDATE`, atomicity guarantees that the debit is undone. No money vanishes.

> [!note] The C in ACID isn't the C in CAP
> ACID consistency means "invariants hold". CAP consistency means linearizability across replicas. Same word, unrelated ideas. Consistency models get their own module.

## Keep the guarantee within its boundary

Atomicity covers transactional database row writes. It does not roll back an email already sent, and sequence values can remain consumed after an abort. A business rule such as "never overdraw" still needs a constraint or concurrency-safe application decision.

## Key takeaways
- Atomicity hides all transactional row changes from an aborted transfer.
- The database enforces declared constraints; the application must encode its other invariants.
- Durability depends on commit configuration, functioning storage and the failures that configuration covers.

## Further reading
- [www.postgresql.org: tutorial transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [PostgreSQL: Write-Ahead Logging](https://www.postgresql.org/docs/current/wal-intro.html)
