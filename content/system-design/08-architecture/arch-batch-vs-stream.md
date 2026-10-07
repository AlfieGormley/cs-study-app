---
id: arch-batch-vs-stream
title: Batch and stream data processing
level: advanced
minutes: 16
summary: How large-scale data processing works, from MapReduce and Spark to stream processors, why Lambda and Kappa architectures exist, and how data lakes, warehouses and lakehouses fit together.
---

Transactional databases commonly support many concurrent users and operational queries. A business also needs to answer questions across **all** the data: daily revenue by region, fraud scores, recommendation models, search ranking signals. That work lives in a separate **data platform**, and it's built from two styles of processing.

| | Batch | Stream |
|---|---|---|
| Input | bounded dataset | unbounded events |
| Latency | Depends on job and scheduling | Depends on processing and trigger policy |
| Example | nightly revenue | fraud alerts |
| Tools | Spark, Hive | Flink, Kafka Streams |

## Batch processing and MapReduce

Google's 2004 **MapReduce** paper described processing large datasets on clusters of commodity machines with a simple programming model.

1. **Map**: each worker reads a chunk of input (say 128 MB of a file on a distributed file system) and emits key–value pairs.
2. **Shuffle**: the framework sorts and groups pairs by key, sending all values for a key to the same reducer, across the network.
3. **Reduce**: each reducer combines the values for its keys.

```
 word count

 chunk1 "a b a"   chunk2 "b c"
    | map             | map
 (a,1)(b,1)(a,1)   (b,1)(c,1)
     \______shuffle______/
      |        |        |
   a:[1,1]  b:[1,1]   c:[1]
      | reduce |        |
    (a,2)    (b,2)    (c,1)
```

What made it work:

- **Move compute to data**: schedule map tasks on the machines that hold the input blocks (Google used GFS; Hadoop uses HDFS replicas), avoiding network transfer.
- **Fault tolerance by re-execution**: with deterministic functions over stable input and framework-managed output commit, failed tasks can be rerun elsewhere. Arbitrary external side effects are not made exactly-once by task retries. Slow "straggler" tasks are run speculatively on a second machine.
- **Immutable inputs, new outputs**: the framework convention is to read stable input and publish new output. User code must avoid unsafe external mutations; the framework does not make every program safe to retry.

The weakness: map output is materialized on local disk and reducer output is written to the distributed file system; reducers can fetch completed map outputs before all maps finish. Chained jobs materialize intermediate results. For multi-stage pipelines and iterative algorithms, materializing intermediates can make I/O a major cost; whether it dominates depends on the workload.

## Spark

**Apache Spark** generalised MapReduce into a **DAG of transformations** over distributed datasets (RDDs, and later DataFrames).

- **In-memory**: chains of per-partition steps are pipelined in memory within a stage, and datasets you reuse can be cached in memory, giving large speed-ups for iterative work. Shuffle data is still written to local disk, but not to the replicated distributed file system between every step as in MapReduce.
- **Lazy evaluation and query optimisation**: transformations build a plan and nothing runs until an action (`count`, `write`) needs a result. For DataFrames and SQL, the Catalyst optimiser rearranges the plan first (pushing filters down, choosing join strategies).
- **Lineage for fault tolerance**: Spark can remember how each partition was computed and recompute lost partitions from their parents. Persistence can also use disk or replication; deterministic transformations and stable sources matter for reproducibility.
- **Narrow vs wide transformations**: map and filter do not themselves redistribute rows; reading input can still use the network. Grouping and joins often need a shuffle, but existing partitioning, broadcasting or storage-partition joins can avoid it. Inspect the physical plan.

> [!warning] Data skew kills batch jobs
> If 30% of rows share one key (say `country = 'US'`, or a null), one task in a shuffle gets 30% of the data while hundreds of others finish in seconds. The job takes as long as that one task. Fixes include salting the hot key, broadcasting the small side of a join, and Spark's adaptive query execution, which splits skewed partitions.

## Stream processing

A stream processor runs continuously over an **unbounded** sequence of events, usually read from a log like Kafka, and emits results as events arrive. Examples: Apache Flink, Kafka Streams, Spark Structured Streaming, Google Dataflow (Apache Beam).

Concepts you can't avoid:

- **Event time vs processing time.** A phone records a tap at 12:00:01 (event time) but is offline, so it reaches you at 12:07 (processing time). Aggregating by processing time puts it in the wrong minute.
- **Windows**: group an infinite stream into finite chunks.
  - *Tumbling*: fixed, non-overlapping (each minute).
  - *Sliding*: overlapping (last 5 minutes, every 1 minute).
  - *Session*: activity separated by gaps of inactivity.
- **Watermarks**: an event-time progress estimate, not a promise that older data cannot arrive. Window triggers and cleanup depend on the engine and allowed-lateness policy; late data can update results, go to a side output or be dropped.
- **State**: counts, joins and windows need state. Flink keeps it locally (often in RocksDB) and periodically takes consistent **checkpoints** to durable storage.
- **Exactly-once** results: Flink can recover internal state consistently using checkpoints and replayable sources. End-to-end effects require a compatible transactional sink or a carefully ordered, versioned idempotent design. An arbitrary external call or plain keyed upsert does not automatically give exactly-once observable behavior.

```
 Kafka --> [Flink job]
   |        keyed state per user
 offsets    | checkpoint every 30s
   |        v
   +--- [S3: state + offsets]
 on failure: restore state, rewind
 offsets, reprocess -> same output
```

## Lambda architecture

Early stream processors were fast but unreliable or approximate. Nathan Marz's **Lambda architecture** (described in 2011, from his work on Storm at BackType and Twitter) ran both paths side by side over the same immutable master dataset:

```
           +--> [batch layer]  --+
 events ---+    (all history,    |
 (immutable|     recompute)      +-> serving
  log)     |                     |   (merge)
           +--> [speed layer] ---+
                (recent, fast,
                 approximate)
```

- The **batch layer** recomputes accurate views from all historical data, say nightly, typically with Hadoop or Spark.
- The **speed layer** covers only the gap since the last batch run, with low-latency, possibly approximate results (originally Storm). Once a batch run covers that period, its speed-layer results are thrown away.
- The **serving layer** indexes the batch views so they can be queried; each query combines the batch view with the speed layer's real-time view.

The appeal is that the batch layer is a safety net. A correct batch recomputation can replace inaccurate recent views once it covers their period. This depends on correct retained input, batch logic and reconciliation; it is not a universal hours-long error bound.

The problem: you write and maintain **the same logic twice**, in two frameworks with different semantics, and debug discrepancies between them forever.

## Kappa architecture

Jay Kreps (co-creator of Kafka) proposed the **Kappa architecture** in his 2014 essay *Questioning the Lambda Architecture*: if your stream processor is reliable and your log retains history, **use one streaming code path for everything**. Batch processing becomes a special case of streaming: a replay of a bounded stretch of the log.

```
 events --> [Kafka, long retention]
                 |
           [stream job v1] --> view_v1
                 |
   reprocess: start [stream job v2]
   from offset 0 --> view_v2, then
   switch readers to view_v2
```

- Recomputation means replaying the log through a new version of the job, not running a separate batch system. The new job writes to a **new output table**; when it has caught up, readers switch to it and the old job and table are deleted.
- One codebase, one set of semantics.
- It requires sufficient retained history, correct state/replay handling and sinks appropriate to the application. Built-in exactly-once support can help but is not a definition of Kappa or a guarantee for arbitrary external side effects.
- The costs: during a reprocess you run two jobs and store two outputs, and Kafka source-reading concurrency is limited by the topic's partitions. Downstream operators can repartition to a different parallelism; source, network, processing and sink throughput all constrain replay. Replaying a year of history through a stream job can take far longer than a batch engine scanning columnar files would.

In practice many organisations run something in between: streaming for fresh, incremental results, and batch for heavy historical backfills, ML training and ad-hoc analysis, increasingly on **unified engines** (Spark, Beam, Flink) where the same code can run in either mode.

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

## Key takeaways
- MapReduce made large-scale batch processing reliable through simple map/shuffle/reduce stages, data locality and re-execution of deterministic tasks over immutable input.
- Spark pipelines and caches data in memory, optimises a DAG of transformations and recovers lost partitions via lineage; shuffles and skew dominate cost.
- Stateful event-time processing uses windows, progress policies and recovery mechanisms. End-to-end correctness also depends on source and sink semantics; not every stream job needs windows or state.
- Lambda runs batch and speed layers in parallel, with batch periodically overwriting the speed layer's recent results, at the cost of duplicated logic. Kappa uses one streaming path and replays the retained log into a new output to recompute.
- Warehouses hold structured columnar data for SQL; lakes hold raw files cheaply; lakehouse table formats add ACID and schemas on top of the lake.

## Further reading
- [Google Research: MapReduce: Simplified Data Processing on Large Clusters](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
- [Apache Spark: RDD programming guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Apache Flink: Timely stream processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)
- [Jay Kreps: Questioning the Lambda Architecture](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
- [Wikipedia: Lambda architecture](https://en.wikipedia.org/wiki/Lambda_architecture)
- [Wikipedia: Data lake](https://en.wikipedia.org/wiki/Data_lake)
- [Apache Iceberg documentation](https://iceberg.apache.org/docs/latest/)
