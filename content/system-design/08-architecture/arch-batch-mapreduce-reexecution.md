---
id: arch-batch-mapreduce-reexecution
title: Processing bounded data with MapReduce
level: advanced
minutes: 3
summary: Trace map, shuffle and reduce while explaining locality and the limits of retry-based recovery.
sourceLesson: arch-batch-vs-stream
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

1. **Map phase**: each worker reads a chunk of input (say 128 MB of a file on a distributed file system) and emits key–value pairs.
2. **Shuffle**: the framework sorts and groups pairs by key, sending all values for a key to the same reducer, across the network.
3. **Reduce phase**: each reducer combines the values for its keys.

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

## Key takeaways
- Bounded historical jobs fit batch; continuously arriving events with prompt result needs fit streams.
- Map emits pairs, shuffle brings equal keys together and reduce combines their values.
- Data locality and deterministic recomputation improve recovery without making arbitrary side effects exactly once.
- Materialising intermediate output adds I/O whose actual cost depends on the workload.

## Further reading
- [Google Research: MapReduce: Simplified Data Processing on Large Clusters](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
