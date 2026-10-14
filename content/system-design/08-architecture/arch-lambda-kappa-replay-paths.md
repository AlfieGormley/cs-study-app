---
id: arch-lambda-kappa-replay-paths
title: Choosing parallel recomputation or replay
level: advanced
minutes: 4
summary: Compare Lambda's batch and speed layers with Kappa's retained-log replay and output cutover.
sourceLesson: arch-batch-vs-stream
---

Stream recovery restores one job. Correcting its business logic requires recomputation; compare two ways to make fresh and historical results coexist.

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
- The **serving layer** indexes the batch views so they can be queried; each query combines the batch view with the speed layer's low-latency view.

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

## Key takeaways
- Lambda combines batch views with a recent speed layer and must reconcile their duplicated logic.
- Kappa rebuilds with a new stream-job version and a separate output before switching readers.
- Recomputation needs sufficient retained history, schemas, code and suitable state/output semantics.
- Source partitions, processing and sink capacity constrain replay; live arrivals consume part of replay throughput.

## Further reading
- [Jay Kreps: Questioning the Lambda Architecture](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
- [Wikipedia: Lambda architecture](https://en.wikipedia.org/wiki/Lambda_architecture)
