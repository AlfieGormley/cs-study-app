---
id: fund-durable-write-batching
title: Trade write acknowledgement latency against loss risk
level: advanced
minutes: 5
summary: Compare PostgreSQL, Kafka and Redis acknowledgement controls, then use batching to share flush costs.
sourceLesson: fund-tradeoffs
---

A successful write response makes a promise. Decide whether it means an in-memory update, a durable local flush or a required replicated commit, then account for the latency of keeping that promise.

## Latency vs durability

When is a write "done"? The earlier you acknowledge it, the faster it is and the more you can lose.

| Acknowledge after... | Additional work | Remaining loss risks |
|---|---|---|
| Written to process memory | Memory update | Process or machine failure before persistence |
| Written to OS page cache | Kernel write | OS crash or power loss before persistence |
| fsync to local durable storage | Storage flush | Storage failure, corruption or later logical deletion |
| Durably replicated to a second zone | Replication acknowledgement | Loss of required durable copies, common failures or logical deletion |
| Durably replicated across regions | Cross-region acknowledgement | Protocol/storage failures, loss of required copies or logical deletion |

> [!note] Content gap: generic durability latency figures
> Exact latency ranges are omitted because no representative measurements support them. Replication is not itself a promise that remote copies are durably flushed; verify the acknowledgement contract and failure model.

Real knobs that control this:

- **Postgres** `synchronous_commit`: the default `on` waits for the WAL to be flushed locally (and, if synchronous standbys are configured, on them too). `off` acknowledges before the flush; a crash can lose up to about three times `wal_writer_delay` of commits (around 600 ms with the 200 ms default), but never corrupts the database. `remote_apply` waits until a synchronous standby has *applied* the commit, so reads there see it. It can be set per transaction.
- **Kafka** producer `acks`: `0` (fire and forget), `1` (leader only), `all` (all in-sync replicas), combined with the topic's `min.insync.replicas`. Kafka 3.0 changed the producer defaults to `acks=all` and idempotence on when settings do not conflict. A bug left idempotence off in 3.0.0 and 3.1.0 unless enabled explicitly; fixes shipped in 3.0.1, 3.1.1 and 3.2.0. `min.insync.replicas` defaults to 1; a value such as 2 with at least 3 appropriately placed replicas improves tolerance of one replica loss, but no setting alone guarantees zero loss under all failures.
- **Redis** persistence: no persistence, RDB snapshots (lose everything since the last snapshot), or the append-only file (AOF) with `appendfsync always` (slow, safest), `everysec` (the usual choice: lose about a second of writes) or `no` (let the OS decide when to flush).

Batching (group commit) softens this trade-off: fsync once for many writes. A log that does one fsync at a time can only do so many per second, and each one can make a whole batch durable:

For an illustrative log whose flush takes 2 ms, serial one-commit flushes allow about 500 commits/s. If each flush makes 50 commits durable, that same flush capacity can cover about 25,000 commits/s. The improvement comes from sharing the expensive flush, rather than weakening the durability acknowledgement.

These illustrative ceilings assume flushes happen one after another and that there are always enough commits waiting to fill a batch. The price is latency: a commit may wait for the next batch, by an amount set by the batching policy, queueing and flush completion time. Kafka and most databases do this, which is why throughput can be high even with durable writes.

## Throughput vs latency

Batching, buffering and compression can improve throughput while adding waiting or CPU work. End-to-end latency can still improve if they reduce a bottleneck:

- Kafka's `linger.ms` can wait to fill an incomplete batch, reducing per-request overhead; measure whether that improves throughput for the workload. Recent versions default it to 5 ms (it was 0 before Kafka 4.0); high-volume producers often raise it further.
- Nagle's algorithm in TCP delays small packets to coalesce them (often disabled with `TCP_NODELAY` for interactive traffic).
- Running servers at high utilisation is cheaper but increases queueing latency, as the latency lesson showed.

## Key takeaways
- The acknowledgement contract determines which crash and storage failures may lose a successful write.
- PostgreSQL commit settings, Kafka acknowledgement and ISR settings, and Redis persistence choices need explicit failure models.
- Group commit shares flush costs across a batch, while batching policy can add per-item waiting.
- Replicated data is not automatically durably flushed, and no single setting covers every failure.

## Further reading
- [Asynchronous commit (PostgreSQL)](https://www.postgresql.org/docs/current/wal-async-commit.html)
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Kafka producer configuration](https://kafka.apache.org/40/configuration/producer-configs/)
- [Kafka historical default changes](https://kafka.apache.org/34/getting-started/upgrade/)
- [Kafka topic durability configuration](https://kafka.apache.org/40/configuration/topic-level-configs/)
