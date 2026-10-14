---
id: msg-stream-checkpoints-changelogs
title: Recover stream state with checkpoints and changelogs
level: advanced
minutes: 3
summary: Keep recovered state consistent with source progress and make sink guarantees match recovery.
sourceLesson: msg-stream-processing
---

A running count and its reading position must recover together. Restoring yesterday’s count while continuing from today’s offset loses work; restoring today’s count but replaying yesterday’s records counts it again.

## Fault-tolerant state

Stateful operators hold a lot of state: millions of keys, each with a running count or a window buffer. It must survive crashes **and** be consistent with the input position, otherwise a restart double-counts.

### Flink: checkpoints

- State lives locally per parallel task, in memory or in **RocksDB** on local disk for large state (terabytes across a cluster is normal).
- Periodically, the JobManager injects **checkpoint barriers** into the sources. In aligned checkpoints, an operator coordinates input barriers and snapshots state to configured durable storage such as S3 or HDFS. Unaligned checkpoints also capture in-flight channel data to reduce alignment delay. This is a variant of the Chandy–Lamport distributed snapshot algorithm.
- A checkpoint records **state plus source offsets** together. On failure, Flink restores every operator from the last checkpoint and rewinds the sources to the matching offsets.
- With transactional sinks (for example, the Kafka sink using two-phase commit tied to checkpoints), this gives end-to-end exactly-once.
- **Flink savepoints** are manually triggered checkpoints for upgrades and rescaling.

### Kafka Streams: changelog topics

- Tasks maintain the stores defined by their topology; persistent stores commonly use RocksDB, while in-memory stores also exist. A task can have multiple stores and inputs.
- Fault-tolerant stores normally use Kafka changelogs; caching/coalescing, source-topic reuse and store configuration affect what is logged. Window-store changelogs also use retention policies. On failure or rebalance, a new instance rebuilds the store by replaying the changelog.
- Rebuilding a large store can take minutes, so **standby replicas** (`num.standby.replicas`) keep warm copies on other instances.
- `processing.guarantee=exactly_once_v2` wraps output, changelog writes and offset commits in a Kafka transaction.

| | Flink | Kafka Streams |
|---|---|---|
| Deploy | Cluster (JobManager) | Library in your app |
| Sources | Many | Kafka only |
| State recovery | Checkpoints to S3 | Changelog topics |
| Good for | Large, complex jobs | Kafka-centric services |

## Key takeaways

- Flink restores state and source offsets from a consistent checkpoint.
- End-to-end exactly-once also requires a replayable source and a sink that coordinates its effects with recovery.
- Kafka Streams restores stores from changelogs; standby replicas reduce large-store restoration pauses.
- Framework guarantees depend on configuration and sink boundaries, not merely enabling state snapshots.

## Further reading

- [Stateful stream processing (Apache Flink docs)](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/)
- [Kafka Streams documentation](https://kafka.apache.org/documentation/streams/)
