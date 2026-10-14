---
id: db-column-store-analytical-work
title: Column stores for analytical work
level: advanced
minutes: 3
summary: Separate analytical scans from transactions and explain column pruning, compression, vectorisation and zone maps.
sourceLesson: db-storage-internals
---

A transaction usually needs a few complete rows. Analytics often needs a few attributes from millions of rows, so it benefits from a different physical layout and execution path.

## OLTP vs OLAP

| | OLTP | OLAP |
|---|---|---|
| Query | Few rows by key | Scan millions |
| Users | Customers, apps | Analysts, BI |
| Writes | Small, random | Bulk loads |
| Data size | GB–TB | TB–PB |

Large analytical scans can harm latency-sensitive OLTP workloads: a big aggregate evicts hot pages from the buffer pool and competes for I/O. That's why analytics moves to a separate **data warehouse**, fed by ETL or CDC.

## Column stores

Row stores keep each row's columns together, which is ideal for "fetch order 42". But an analytical query like

```sql
-- Read only the attributes this report
-- needs.
SELECT region, sum(revenue_p)
FROM sales
WHERE sale_date >= '2026-01-01'
GROUP BY region;
```

assumes an existing sales table and returns one aggregate per matching region; values depend on the rows. It reads only 3 columns of a 100-column table. A full row-store heap scan reads pages containing the other columns too, but covering indexes, cache residency and projections can change the I/O comparison.

A **column store** keeps each column in its own file (or segment):

```
 row store:   [id,date,region,rev,...]
              [id,date,region,rev,...]

 column store:
   date:   [d1 d2 d3 d4 ...]
   region: [UK UK UK FR ...]
   rev:    [12 40  7 33 ...]
```

Benefits:

- **Read only the needed columns**: 3 of 100 equally sized columns would mean roughly 97% less uncompressed column data. Actual I/O savings depend on column sizes, compression, indexes and row-group pruning.
- **Compression**: a column holds similar values. Run-length encoding (`UK×3`), dictionary encoding and bit-packing can compress repeated or correlated values; the ratio depends on the dataset and encoding.
- **Vectorised execution**: processing a batch of values from one column in a tight loop uses CPU caches and SIMD instructions efficiently.
- **Zone maps**: min/max per block let the engine skip blocks that can't match `sale_date >= '2026-01-01'`.

Costs: a pure column layout may update many column chunks, so many column stores batch writes (often via an in-memory row buffer, LSM-style) and are poor at single-row updates.

Examples: Snowflake, BigQuery (Capacitor format, Dremel engine), Amazon Redshift, ClickHouse, Apache Druid, DuckDB, and file formats like **Parquet** and ORC. Some databases are hybrids (HTAP): SQL Server columnstore indexes, TiDB with TiFlash, SingleStore.

## Key takeaways
- Large analytical scans compete with transaction latency for memory and I/O.
- Column layouts read only needed attributes and can compress and process values in batches.
- Zone maps prune blocks effectively when their value ranges are narrow; point updates have different costs.

## Further reading
- [clickhouse.com: intro](https://clickhouse.com/docs/intro)
- [clickhouse.com: parts](https://clickhouse.com/docs/parts)
- [parquet.apache.org: overview](https://parquet.apache.org/docs/overview/)
