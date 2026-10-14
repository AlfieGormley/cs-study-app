---
id: db-normalisation-read-models
title: Normalisation and deliberate read models
level: basic
minutes: 3
summary: Remove duplicated facts, preserve historical prices, and maintain deliberate copies without losing correctness.
sourceLesson: db-relational-acid
---

A fact copied into many rows is difficult to change consistently. Start by separating facts, then duplicate only a measured read path with a clear synchronisation rule.

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

Normalised data needs joins to reassemble. At large scale, or when one read path dominates, you may deliberately denormalise: duplicate data so that reads are cheaper.

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

## Measure the read path before sharding

If a primary is busy mostly answering reads, first investigate the slow query plans and suitable indexes. A cache and read replicas can offload eligible reads while writes remain on the primary. This adds freshness and failure trade-offs, covered in the replication units; do not send reads that require current primary state to a stale replica. Write rate or dataset size alone does not establish that sharding is necessary.

## Key takeaways
- Normal forms avoid partial-key and transitive dependencies that create update anomalies.
- A purchase price and a current catalogue price are different facts.
- Update transactional counters with their source writes; measure read bottlenecks before distributing data.

## Further reading
- [PostgreSQL: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [www.postgresql.org: performance tips](https://www.postgresql.org/docs/current/performance-tips.html)
- [PostgreSQL: Hot standby](https://www.postgresql.org/docs/current/hot-standby.html)
