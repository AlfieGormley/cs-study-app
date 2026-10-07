---
id: rel-th-denormalisation
title: Denormalisation trade-offs
level: advanced
minutes: 13
summary: When storing redundant data is worth it, the main techniques (copied columns, counters, summary tables, materialised views, star schemas, embedded documents), how to keep copies in sync, and the failure modes.
---

Normalisation stores every fact once, which makes writes simple and keeps the data consistent. The price is paid on reads: answering a question may mean joining several tables.

**Denormalisation** is deliberately storing a fact more than once, or storing something derivable, so that reads get cheaper. It is not the absence of design. A denormalised schema starts from a normalised one and adds controlled redundancy, together with a plan for keeping the copies in agreement.

The rule of thumb: **normalise until it hurts, denormalise until it works**. And measure before you decide it hurts.

## First, check you actually need it

Joins on indexed keys can be efficient, but their cost depends on row counts, selectivity, caching and the selected join algorithm. A Postgres primary-key lookup takes a few B-tree page reads, usually cached, and joining an order to its customer by key adds one more such lookup per row. Teams often denormalise to fix a slow query whose real problem was something else. Before adding redundancy, try:

1. **An index** on the join or filter column. Missing indexes on foreign keys can slow selective joins or parent-row changes, since Postgres does not create them automatically.
2. **A covering index** (`CREATE INDEX ... INCLUDE (...)`) which can enable an index-only scan; PostgreSQL may still fetch heap pages for visibility checks.
3. **Fixing the query**: an N+1 loop in the application, a function on an indexed column, or fetching far more rows than needed.
4. **A cache** in front of the database, which is redundancy too but lives outside the schema.

If the read is still too slow, or is run so often that its cost dominates, denormalise.

## The techniques

### 1. Copying a column

Store a value from a parent row on its children, so a common read avoids a join:

```
orders(id, customer_id,
       customer_name,  -- copied
       total, ...)
```

Every change to `customer.name` must now also update that customer's orders. If one customer has 50,000 orders, a rename becomes a 50,000-row write.

> [!warning] Snapshot or cache?
> Ask whether the copy should follow the original. The shipping address *on an invoice* should **not** change when the customer moves: it is a historical fact about the order, and storing it is correct normalised design. A copy of the customer's *current* display name **should** follow the original: that is a cache, and true denormalisation. Confusing the two either rewrites history or leaves stale data.

### 2. Precomputed counts and totals

`post.comment_count` saves a `COUNT(*)` over comments on every page view. If a post page is read 1,000 times a second and gets 5 comments a second, you trade 1,000 counts for 5 increments.

A trigger keeps it in step within the same transaction:

```sql
CREATE FUNCTION bump_count()
RETURNS trigger AS $$
BEGIN
  UPDATE post
     SET comment_count = comment_count + 1
   WHERE id = NEW.post_id;
  RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER comment_ins
AFTER INSERT ON comment
FOR EACH ROW EXECUTE FUNCTION bump_count();
```

(A real version also handles `DELETE` and posts moving.) The hidden cost is **contention**. Every comment on a viral post updates the same row, and each `UPDATE` holds that row's lock until its transaction commits, so writers queue behind one another. Remedies: split the counter into N rows and sum them on read (sharded counters), or buffer increments and apply them in batches.

### 3. Summary tables and materialised views

Reports such as daily sales per product scan millions of rows. Precompute them:

```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT o.day, l.product_id,
       SUM(l.qty * l.price_paid) AS revenue
FROM orders o JOIN line l
  ON l.order_id = o.id
GROUP BY o.day, l.product_id;

CREATE UNIQUE INDEX
  ON daily_sales (day, product_id);

REFRESH MATERIALIZED VIEW
  CONCURRENTLY daily_sales;
```

In Postgres, a materialised view is a stored query result. It does not update itself; `REFRESH` re-runs the whole query. Plain `REFRESH` locks out readers while it runs; `CONCURRENTLY` lets reads continue but needs a unique index on the view and does more work. Core Postgres has no incremental refresh (extensions such as `pg_ivm` add it), whereas Oracle's fast-refresh materialised views and SQL Server's indexed views maintain results incrementally, with restrictions on the query shape.

The view is as stale as its last refresh. That suits a dashboard refreshed every 15 minutes; it does not suit a stock level shown at checkout.

### 4. Star schemas in warehouses

Analytical databases denormalise on purpose. A **star schema** has a central **fact table** (one row per sale, with numeric measures and foreign keys) surrounded by wide, denormalised **dimension tables**:

```
          dim_date
             |
dim_store - fact_sales - dim_product
             |
         dim_customer
```

`dim_product` holds product, category and department names in one row, even though category → department is a transitive dependency. The **snowflake** variant normalises dimensions back out. Stars can help when controlled data-loading pipelines keep duplicated dimension attributes consistent; batch loading alone does not prevent update anomalies and queries join one big table to a few small ones, which columnar engines handle well.

### 5. Embedding and single-table design

Document and key-value stores push this furthest. In MongoDB you might embed an order's lines inside the order document. In DynamoDB, which has no joins, a common pattern stores several entity types in one table, keyed so that one query fetches a customer and their recent orders together. AWS's own guidance is to design around your access patterns first, which is denormalisation as the default. The cost is the same as in SQL: duplicated data must be updated in every place, and changing an access pattern can mean rewriting the data.

### 6. Same-row derived values

A value computed from other columns *in the same row* is the cheapest kind, because there is no fan-out. Postgres generated columns do it declaratively:

```sql
ALTER TABLE line ADD COLUMN amount
  NUMERIC GENERATED ALWAYS AS
  (qty * price_paid) STORED;
```

`STORED` computes on write and can be indexed. Postgres 18 added `VIRTUAL` generated columns (now the default), computed on read.

## Keeping copies consistent

Every denormalisation needs an answer to "what updates the copy, and how stale may it be?"

| Mechanism | Staleness | Main risk |
|---|---|---|
| Same transaction | none | slower writes |
| Trigger | none | hidden logic |
| CDC / outbox | asynchronous; often seconds, unbounded during failures | lag, ordering |
| Batch refresh | minutes+ | stale reads |

- **Application code in the same transaction** is explicit, but every code path that writes the source must remember the copy. One forgotten admin script causes drift.
- **Enabled triggers** automatically run for their configured events, but uncovered operations or disabled triggers can still leave gaps; but they are invisible to someone reading the application, can cascade, and add lock contention.
- **Change data capture** (reading the write-ahead log, for example with Debezium) or a transactional outbox propagates changes asynchronously to other tables, search indexes or services. Writes stay fast, readers see eventual consistency.
- **Batch rebuilds** (materialised view refresh, nightly jobs) are simple and self-healing, at the cost of staleness.

Whatever you choose, add a **reconciliation check**: a periodic query comparing the copy with the source, such as counts that disagree with `COUNT(*)`. Drift happens, through bugs, manual fixes and restores, and you want to find it before customers do.

## The trade-off in one picture

```
            normalised   denormalised
reads       more joins   fewer joins
writes      one place    many places
integrity   by schema    by your code
change      easy         harder
storage     less         more
```

Denormalise when reads vastly outnumber writes to the copied data, the read path is measured to be the bottleneck, and some staleness is acceptable or the sync can be transactional. Avoid it for data that changes often and is copied widely (a username copied into millions of messages), or where a stale value causes real harm (balances, stock).

## Key takeaways
- Denormalisation adds controlled redundancy to a normalised design to speed reads; every copy needs an owner that keeps it in sync.
- Try indexes, covering indexes and query fixes first; joins on indexed keys are cheap.
- Distinguish historical snapshots (correct design) from cached copies (true denormalisation).
- Counters cause hot-row contention; materialised views in Postgres refresh in full and are only as fresh as the last refresh; star schemas denormalise dimensions for analytics.
- Choose a sync mechanism by acceptable staleness, and run reconciliation checks to catch drift.

## Further reading
- [Denormalization — Wikipedia](https://en.wikipedia.org/wiki/Denormalization)
- [Materialized views — PostgreSQL documentation](https://www.postgresql.org/docs/current/rules-materializedviews.html)
- [Generated columns — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl-generated-columns.html)
- [Star schema — Wikipedia](https://en.wikipedia.org/wiki/Star_schema)
- [NoSQL design for DynamoDB — AWS documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html)
