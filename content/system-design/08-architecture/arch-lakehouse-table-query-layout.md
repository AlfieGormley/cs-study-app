---
id: arch-lakehouse-table-query-layout
title: Adding table semantics to lake files
level: advanced
minutes: 3
summary: Compare warehouses, lakes and lakehouses while connecting column pruning and table snapshots to query reliability.
sourceLesson: arch-batch-vs-stream
---

Batch and stream jobs both need durable inputs and reliable analytical outputs. The file layout and table metadata determine which bytes a query reads and which committed snapshot it observes.

## Data lakes, warehouses and lakehouses

Where does all this data live?

- A **data warehouse** (Snowflake, BigQuery, Redshift) provides managed analytical queries, commonly using columnar storage. It can hold raw and semi-structured as well as cleaned data; schema behavior depends on its table and data types. Columnar storage means a query that sums one column out of 200 reads only that column, compressed.
- A **data lake** stores raw files of any type (JSON, CSV, Parquet, images, logs) cheaply in object storage like S3. Schema is applied on read. It's flexible but can become a "data swamp" without cataloguing and quality controls.
- A **lakehouse** adds a **table format** (Apache Iceberg, Delta Lake, Apache Hudi) over data files in the lake, often Parquet (Iceberg also supports Avro and ORC), providing table-level commit/snapshot mechanisms, schema evolution and metadata used by compatible engines. Exact transaction scope and retained time-travel history depend on the format, catalog, engine and configuration, so warehouse-style SQL engines can query lake data reliably.

```
 OLTP DBs --CDC-+
 app events ----+--> [Kafka] -> streams
 3rd party -----+       |
                         v
            [lake: S3 + Iceberg tables]
              raw -> cleaned -> aggregated
                         |
           [SQL engines / warehouse / ML]
```

A common layering is **bronze** (raw), **silver** (cleaned, deduplicated, conformed) and **gold** (business-level aggregates).

> [!note] ETL vs ELT
> Classic **ETL** transforms data *before* loading it into the warehouse. Modern **ELT** loads raw data first and transforms it inside the warehouse or lakehouse with SQL (often with dbt), because storage is cheap and compute is elastic.

## Choosing

- Need results within seconds (fraud, alerting, live dashboards, feature updates)? **Stream.**
- Processing large historical datasets, training models, or results needed daily? **Batch.**
- Both, with one codebase? **Kappa-style streaming plus replay**, or a unified engine.
- Retain sufficient raw data or suitable snapshots for the required rebuild horizon, subject to deletion and retention requirements. Reproducible replay also needs relevant schemas, code and external inputs.

### A query-layout thought experiment

Suppose a table has equal-sized columns and equal daily volumes. A one-column query needs only that column in columnar files; a date-partitioned layout can then exclude unrelated days before reading data. Compression reduces the remaining payload further. These savings multiply in the ideal model used by the question, but real queries also read metadata and may need predicate columns, row groups or extra pages. They are not a production benchmark. A table format contributes snapshot and schema rules; it does not automatically guarantee good file sizes, cataloguing or query plans.

## Key takeaways
- Warehouses provide analytical query services; lakes store raw files; lakehouse formats define tables over those files.
- Columnar layout, date partition pruning and compression reduce payload reads under explicit workload assumptions.
- Compatible readers use committed table metadata rather than treating arbitrary file listings as a transaction.
- Retain suitable raw data and reproducibility inputs for the required rebuild horizon.

## Further reading
- [Wikipedia: Data lake](https://en.wikipedia.org/wiki/Data_lake)
- [Apache Iceberg documentation](https://iceberg.apache.org/docs/latest/)
