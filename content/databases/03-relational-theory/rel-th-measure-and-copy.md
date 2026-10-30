---
id: rel-th-measure-and-copy
title: Measuring redundancy and copied values
level: advanced
minutes: 3
sourceLesson: rel-th-denormalisation
summary: Denormalisation as controlled redundancy: measure first, and tell historical snapshots from cached copies.
---

Normalisation stores every fact once, which makes writes simple and keeps the data consistent. The price is paid on reads: answering a question may require joining several tables.

**Denormalisation** is deliberately storing a fact more than once, or storing something derivable, so that reads get cheaper. It is not the absence of design. A denormalised schema starts from a normalised one and adds controlled redundancy, together with a plan for keeping the copies in agreement.

The rule of thumb: **normalise until it hurts, denormalise until it works**. And measure before you decide it hurts.

## First, check you actually need it

Joins on indexed keys can be efficient, but their cost depends on row counts, selectivity, caching and the selected join algorithm. A primary-key index can support selective lookups, but a join need not do one lookup per order: the planner may choose a hash, merge or nested-loop join. Cache state, selectivity and output size determine the measured cost. Teams often denormalise to fix a slow query whose real problem was something else. Before adding redundancy, try:

1. **An index** on the join or filter column. Missing indexes on foreign keys can slow selective joins or parent-row changes, since Postgres does not create them automatically.
2. **A covering index** (`CREATE INDEX ... INCLUDE (...)`) which can enable an index-only scan; PostgreSQL may still fetch heap pages for visibility checks.
3. **Fixing the query**: an N+1 loop in the application, a function on an indexed column, or fetching far more rows than needed.
4. **A cache** in front of the database, which is redundancy too but lives outside the schema.

If the read is still too slow, or is run so often that its cost dominates, denormalise.

## Copied current values and historical facts

Store a value from a parent row on its children, so a common read avoids a join:

```
orders(id, customer_id,
       customer_name,  -- copied
       total, ...)
```

Every change to `customer.name` must now also update that customer's orders. If one customer has 50,000 orders, a rename becomes a 50,000-row write.

> [!warning] Snapshot or cache?
> Ask whether the copy should follow the original. The shipping address *on an invoice* should **not** change when the customer moves: it is a historical fact about the order, and storing it is correct normalised design. A copy of the customer's *current* display name **should** follow the original: that is a cache, and true denormalisation. Confusing the two either changes history or leaves stale data.

> [!analogy] Real-world analogy: a till receipt and a phone contact
> A till receipt records the price you paid and the shop's address on the day. If the shop later raises prices or moves, your receipt must not change. The contact entry for a friend on your phone is different: when they change number, you want your copy updated, and a stale copy is simply wrong.
>
> **How it maps:** The receipt is a historical snapshot stored with the event (the invoice's shipping address, the price paid on an order line); it is its own fact, not redundancy. The phone contact is a cached copy of a current value (a customer's display name copied onto orders), which must follow its source.
>
> **Where it stops:** You fix one contact by hand when you hear about a change. A database copy may sit on millions of rows, so every change to the source becomes a large write, and nothing updates the copies unless you build and test the mechanism that does.

## Key takeaways

- Measure the query and its plan before adding copied-value update fan-out.
- Historical snapshots model a different fact; a cached current value must follow its source.

## Further reading

- [PostgreSQL 18: refresh materialised views](https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html)
- [PostgreSQL 18: generated columns](https://www.postgresql.org/docs/18/ddl-generated-columns.html)
- [AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [PostgreSQL 18: covering indexes and index-only scans](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)
