---
id: arch-spark-shuffle-skew-plans
title: Understanding Spark stages and skew
level: advanced
minutes: 3
summary: Read a lazy transformation plan and diagnose the hot task that dominates a shuffle stage.
sourceLesson: arch-batch-vs-stream
---

MapReduce groups matching keys on reducers. Spark extends this into stages of a dependency graph; the physical plan reveals where redistribution and hot keys dominate.

## Spark

**Apache Spark** generalised MapReduce into a **DAG of transformations** over distributed datasets (RDDs, and later DataFrames).

- **In-memory**: chains of per-partition steps are pipelined in memory within a stage, and datasets you reuse can be cached in memory, giving large speed-ups for iterative work. Shuffle data is still written to local disk, but not to the replicated distributed file system between every step as in MapReduce.
- **Lazy evaluation and query optimisation**: transformations build a plan and nothing runs until an action (`count`, `write`) needs a result. For DataFrames and SQL, the Catalyst optimiser rearranges the plan first (pushing filters down, choosing join strategies).
- **Lineage for fault tolerance**: Spark can remember how each partition was computed and recompute lost partitions from their parents. Persistence can also use disk or replication; deterministic transformations and stable sources matter for reproducibility.
- **Narrow vs wide transformations**: map and filter do not themselves redistribute rows; reading input can still use the network. Grouping and joins often need a shuffle, but existing partitioning, broadcasting or storage-partition joins can avoid it. Inspect the physical plan.

> [!warning] Data skew kills batch jobs
> If many rows share one key and the physical plan sends them to one task without first reducing or splitting them, that task can dominate completion time.

A stage cannot finish until its slowest required task finishes. Giving a hot key to one task can leave most workers idle while that task continues.

Adding workers alone does not divide an indivisible hot-key task. The right fix depends on the operation and physical plan.

### Match the fix to the operator

For a mergeable SUM aggregation, salt a hot key into several partial groups, sum each group, then combine the partial sums by the original key. This preserves the result while spreading the first aggregation. It is not a generic transformation for arbitrary non-mergeable calculations. Spark's adaptive skew-join splitting addresses supported joins; it should not be described as automatically fixing every skewed aggregation. Inspect the actual task metrics and plan before adding executors.

## Key takeaways
- Spark builds a lazy DAG and can pipeline or cache work; shuffle data still incurs disk and network costs.
- Lineage can reconstruct lost partitions when inputs and transformations remain reproducible.
- Grouping or joins may shuffle unless a compatible plan avoids redistribution.
- Skew concentrates work in a long task; salt mergeable aggregates or use appropriate join strategies.

## Further reading
- [Apache Spark: RDD programming guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Apache Spark: SQL performance tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
