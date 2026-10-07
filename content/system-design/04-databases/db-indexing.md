---
id: db-indexing
title: Indexing
level: intermediate
minutes: 14
summary: B-trees versus LSM trees, composite and covering indexes, and what every index costs on writes.
---

Without a suitable access path, a database may need a full scan; partition pruning, zone maps or other mechanisms can sometimes reduce it. An **index** is an extra data structure, kept in sync with the table, that lets the database jump straight to the matching rows. Indexes can substantially reduce work for selective queries, but add storage and write cost.

## The cost of not having one

Take a 100 million row `orders` table on 8 KB pages, about 100 rows per page: one million pages, or 8 GB. A full scan at 1 GB/s takes around 8 seconds. A B-tree lookup touches 3–4 pages: well under a millisecond if they're cached.

## B-trees

The **B-tree** (strictly, the B+tree) is the default index in Postgres, MySQL InnoDB, SQL Server, Oracle and SQLite.

```
            [ 40 | 80 ]          root
          /      |      \
   [10|25]   [50|65]   [90|99]   internal
   / | \      / | \      / | \
  leaves: sorted keys + row pointers,
  linked left to right for range scans
```

- Each node is one **page** (typically 4–16 KB) holding hundreds of keys, so the tree is very wide and shallow. With a fan-out of 500, four levels address 500⁴ ≈ 62 billion keys.
- Lookups walk root → leaf: O(log n), usually 3–4 page reads, and the top levels are almost always in memory.
- Leaves are sorted and linked, so **range scans** (`BETWEEN`, `>`, `ORDER BY`) are efficient.
- Writes **update pages in place**. Inserting into a full page *splits* it into two. To survive crashes, every change is first written to the write-ahead log (see the storage internals lesson).

In InnoDB, the table *is* a B-tree clustered on the primary key, and secondary indexes store the primary key as their pointer. In Postgres, the table is an unordered heap and every index points to a physical tuple location.

That design choice has practical consequences in InnoDB:

- A non-covering secondary-index lookup generally needs two B-tree walks: find the primary key in the secondary index, then find the row in the clustered index.
- Every secondary index entry carries a copy of the primary key, so a wide key (a 36-character UUID string) bloats every index.
- Rows are stored in key order, so random keys (UUIDv4) insert all over the tree and cause page splits, while increasing keys (auto-increment, or time-ordered UUIDv7) append at the right-hand edge.
- Such a query is covered by the secondary index, but InnoDB may still visit the clustered record for MVCC visibility.

## LSM trees

The **log-structured merge tree** takes the opposite approach: never update in place, always append.

```
 write ─► WAL + memtable (sorted, in RAM)
              │ flush when full
              ▼
 L0: [SST] [SST] [SST]     newest
 L1: [ SST ][ SST ][ SST ]
 L2: [  SST  ][  SST  ]... oldest
     background compaction merges
     and drops overwritten keys
```

1. Writes go to an append-only log (for durability) and an in-memory sorted structure, the **memtable**.
2. When the memtable fills (say 64 MB), it's written out as an immutable sorted file, an **SSTable**.
3. Background **compaction** merges SSTables, discarding overwritten values and deletion markers (*tombstones*).
4. Reads check the memtable, then SSTables from newest to oldest. **Bloom filters** let a read skip files that definitely don't contain the key.

LSM trees power RocksDB, LevelDB, Cassandra, ScyllaDB, HBase, Bigtable, and the storage layers of CockroachDB, TiDB and YugabyteDB.

| | B-tree | LSM tree |
|---|---|---|
| Writes | Random, in place | Sequential, batched |
| Reads | One place to look | Several levels |
| Space | Pages part-empty | Old versions until compacted |
| Latency | Predictable | Compaction spikes |

> [!note] Rule of thumb
> B-trees favour reads and predictable latency; LSM trees favour write throughput and compression. Both are excellent; the details are in the storage internals lesson.

## Composite indexes

A **composite** (multi-column) index sorts by the first column, then by the second within ties, and so on, like a phone book sorted by surname then first name.

```sql
CREATE INDEX idx_orders_cust_date
  ON orders (customer_id, created_at);
```

This index serves:

- `WHERE customer_id = 42`
- `WHERE customer_id = 42 AND created_at > '2026-09-01'`
- `WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 20` with no sort step

With many distinct customers, it may not efficiently serve `WHERE created_at > '2026-09-01'` alone, because entries for that date range are scattered across every customer. This is the **leftmost-prefix rule**.

Some engines soften the rule with a **skip scan** (MySQL 8.0, Oracle, and Postgres from version 18): when the leading column has only a few distinct values, they probe the index once per value. With millions of customers that doesn't help, so design the index for the query rather than relying on it.

> [!tip] Column order: equality first, then range
> Put columns tested with `=` first and the range or sort column last. With `(created_at, customer_id)`, a conventional scan may cover September entries for many customers; skip scan and other planner choices can change that.

## Covering indexes

Normally an index lookup finds a row pointer, then fetches the row from the table: an extra random read per row. If the index contains *every column the query needs*, the database can answer from the index alone. That's a **covering index**, and Postgres calls the resulting plan an *index-only scan*.

```sql
CREATE INDEX idx_orders_cover
  ON orders (customer_id, created_at)
  INCLUDE (total_p, status);

SELECT created_at, total_p, status
FROM orders
WHERE customer_id = 42
ORDER BY created_at DESC LIMIT 20;
```

`INCLUDE` adds non-key payload columns to the leaves without affecting sort order. For a query returning 20 rows, that can avoid heap visits when the visibility conditions permit; avoided visits are not necessarily physical disk reads.

In Postgres, index-only scans also depend on the **visibility map**: if a page has recent, unvacuumed changes, Postgres still visits the heap to check row visibility. Keep autovacuum healthy on tables where you rely on them.

## Other index types

- **Hash** indexes: equality only, no ranges. Rarely better than a B-tree in Postgres.
- **Partial** indexes: index only the rows you query, e.g. `WHERE status = 'pending'`. Much smaller.
- **Expression** indexes: `ON users (lower(email))` serves `WHERE lower(email) = ...`.
- **GIN** (inverted): for `jsonb`, arrays and full-text search.
- **GiST/SP-GiST, BRIN**: geometric data, and very large naturally ordered tables (BRIN stores min/max per block range and is tiny).

## The cost of indexes on writes

Each index adds maintenance for writes affecting its entries; partial indexes and HOT updates are important exceptions.

- An `INSERT` into a Postgres heap table with 6 B-tree indexes inserts one heap tuple and 6 index entries; InnoDB uses a clustered B-tree for the table itself. Each structure adds buffer, I/O and WAL work.
- An `UPDATE` touching an indexed column updates that index too. In Postgres, updating *any* column covered by a B-tree (or other non-summarising) index prevents a **HOT** (heap-only tuple) update, so ordinary indexes need entries for the new tuple version; summarizing indexes such as BRIN have different maintenance. HOT also needs free space on the same page, which is why hot tables often use a `fillfactor` below 100.
- Indexes consume memory. If they don't fit in the buffer cache, lookups and inserts start hitting disk.
- More indexes give the planner more choices, which occasionally means a bad choice.

> [!warning] Audit unused indexes
> In Postgres, `pg_stat_user_indexes.idx_scan = 0` means no scans were recorded in the observed statistics window; it does not mean the index has no purpose. Before dropping one, check statistics resets, replicas, rare jobs and especially uniqueness, primary-key or exclusion constraints. Constraint enforcement is a reason to keep an index even without query scans.

## Why an index might not be used

- The query wraps the column in a function: `WHERE date(created_at) = ...` can't use an index on `created_at`. Rewrite as a range.
- Low selectivity: if 40% of a 100-million-row table matches, a sequential scan of its million pages is cheaper than 40 million index lookups that jump around the heap. The crossover is often at a few percent of rows, and depends on how well the table's physical order matches the index.
- Type mismatch: comparing a text column to an integer forces a cast.
- Leading wildcard: `LIKE '%smith'` can't use a B-tree (use a trigram GIN index).
- Stale statistics: run `ANALYZE` so the planner knows the data distribution.

## Key takeaways
- B-trees update fixed-size pages in place and give O(log n) lookups in 3–4 page reads; LSM trees append, flush sorted files and compact in the background.
- Composite indexes follow the leftmost-prefix rule: put equality columns first, range or sort columns last.
- Covering indexes can avoid table visits, subject to visibility checks and the chosen plan.
- Every index slows writes, uses memory, and must earn its keep; drop unused ones.
- Use `EXPLAIN ANALYZE` to confirm an index is actually used.

## Further reading
- [PostgreSQL: Multicolumn indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
- [PostgreSQL: Index-only scans and covering indexes](https://www.postgresql.org/docs/current/indexes-index-only-scans.html)
- [Use The Index, Luke: concatenated indexes](https://use-the-index-luke.com/sql/where-clause/the-equals-operator/concatenated-keys)
- [Wikipedia: Log-structured merge-tree](https://en.wikipedia.org/wiki/Log-structured_merge-tree)
- [RocksDB Overview](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview)
- [MySQL: Clustered and secondary indexes](https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html)
- [PostgreSQL: Partial indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
