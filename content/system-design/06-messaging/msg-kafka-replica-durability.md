---
id: msg-kafka-replica-durability
title: Kafka replication, ISR and durable acknowledgements
level: intermediate
minutes: 4
summary: Combine replication factor, the in-sync minimum and producer acknowledgements without trusting unsafe defaults.
sourceLesson: msg-kafka-log-streaming
---

A successful publish is only as durable as the acknowledgement rule behind it. Read the producer setting together with the topic’s in-sync replica minimum and the cluster’s failure state.

## Replication and the ISR

Each partition has a **replication factor** (typically 3). One replica is the **leader**; all reads and writes go through it by default. **Followers** fetch from the leader to stay up to date.

```
P0: leader b1, followers b2, b3
producer ─▶ b1 ──fetch── b2
             └──fetch── b3
```

The **in-sync replica set (ISR)** is the leader plus the followers that have caught up within `replica.lag.time.max.ms` (default 30 s). A record is **committed** when every replica in the ISR has it. The **high watermark** is the offset up to which records are committed; consumers can only read up to it.

Durability comes from combining three settings:

| Setting | Typical safe value |
|---|---|
| `replication.factor` | 3 |
| `min.insync.replicas` | 2 |
| producer `acks` | `all` |

With `acks=all`, the leader acknowledges only when all **current** ISR members have the record. `min.insync.replicas` sets a floor on how many replicas that must be. The leader checks it before accepting each `acks=all` write:

```formula
|ISR| ≥ m
where
|ISR|: the number of replicas currently in the in-sync replica set, counting the leader itself
ISR: the in-sync replica set
m: the topic's min.insync.replicas setting (broker default 1; 2 is the usual safe choice)
≥: is greater than or equal to
In words: an acks=all write is accepted only while at least m replicas are in sync; otherwise the leader refuses it.
```

So `min.insync.replicas=2` makes the leader **refuse writes** (with `NotEnoughReplicas`) if the ISR shrinks below 2: with 3 replicas, one follower can drop out (|ISR| = 2) and writes continue, but if both drop out (|ISR| = 1) writes are refused. Together they guarantee an acknowledged write is on at least two brokers. With all three replicas initially healthy and controller quorum available, it tolerates one replica failure without losing acknowledged data and can resume writes after detection/election. Transient write errors or pauses are still possible.

Since **Kafka 3.0** the producer defaults are already safe: `acks=all` and `enable.idempotence=true`. But the broker default for `min.insync.replicas` is still **1**. If both followers fall behind and drop out of the ISR, the ISR is just the leader, and `acks=all` is satisfied by the leader alone. A write acknowledged in that state is guaranteed on only one broker; follower copies may or may not exist, and Kafka replication acknowledgement is not a per-write fsync guarantee. Set `min.insync.replicas=2` explicitly on topics that matter.

With `acks=1` (the default before 3.0), the leader acknowledges as soon as it has written locally. If it dies before followers fetch, the acknowledged write is lost when a follower becomes leader. With `acks=0` the producer does not wait at all.

> [!note] Unclean leader election
> If no ISR replica is available, eligible-leader-replica (ELR) tracking in newer Kafka can identify other safe candidates. Without a safe candidate, Kafka must wait or permit unclean election that risks data loss. `unclean.leader.election.enable` defaults to `false`: Kafka chooses consistency.

Cluster metadata, including which broker leads each partition and the ISR of every partition, is managed by the **KRaft** controller quorum: a small set of controller nodes (typically 3 or 5) that replicate a metadata log among themselves using a Raft-style protocol. One controller is active; brokers follow the metadata log and apply changes. KRaft became production-ready in Kafka 3.3, and **ZooKeeper support was removed entirely in Kafka 4.0** (2025), so clusters must migrate to KRaft on 3.x before upgrading. Like any majority quorum, 3 controllers tolerate one failure and 5 tolerate two.

## Key takeaways

- acks=all waits for the current ISR, whose size can shrink; it does not mean every configured replica.
- An explicit minimum of two in-sync replicas prevents acknowledged writes on the leader alone.
- A surviving leader can serve previously committed records while insufficient ISR size blocks writes.
- Kafka 4.x metadata lives in KRaft; leader-election safety and controller quorum availability remain part of recovery.

## Further reading

- [Apache Kafka documentation: design](https://kafka.apache.org/documentation/)
- [Kafka replication design (Confluent docs)](https://docs.confluent.io/kafka/design/replication.html)
