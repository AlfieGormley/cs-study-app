---
id: fund-quorum-read-guarantees
title: Describe actual read guarantees and quorum overlap
level: advanced
minutes: 4
summary: Use Cassandra and ZooKeeper to distinguish quorum intersection, freshness and linearisability.
sourceLesson: fund-cap-pacelc
---

PACELC classifications summarise choices, but a concrete operation needs a concrete guarantee. Replica counts and read behaviour explain why two systems with the same broad label can expose different values.

## Concrete read guarantees

- **Cassandra** with `ONE` reads and writes favours availability and low latency when at least one actual replica for the key is reachable, but can still time out or reject requests. With `QUORUM` reads and writes, it pays latency for stronger guarantees (though it still isn't fully linearisable without lightweight transactions). The rule behind this, quorum overlap, is worked through below.

- **etcd** serves linearisable reads by default, confirming with a quorum before answering. **ZooKeeper** commits writes through a quorum, but by default a client reads from whichever server it's connected to, which may lag: reads are ordered but can be stale. `sync()` is a useful freshness barrier, but is not a quorum operation and is not a strict linearisability guarantee under all failures. Same "CP" label, different everyday guarantee.

## Quorum overlap

In a leaderless store like Cassandra, each key is copied to several replicas. A write is reported successful once some of them acknowledge it, and a read asks some of them and takes the newest answer. For a completed write and a subsequent read over the same fixed replica set, the groups must overlap when their combined replica counts exceed the number of replicas. This is an intersection guarantee; timestamps, concurrent updates and partially applied writes still affect which value is returned.

```formula reference
W + R > N
Q = ⌊N / 2⌋ + 1
where
N: number of replicas for the key in the fixed replica set
W: number of replicas acknowledging the completed write
R: number of replicas consulted by the subsequent read
Q: number in a majority quorum
⌊ ⌋: floor, rounding down to a whole number
>: is greater than
In words: read and write groups must overlap if their combined sizes exceed the replica count. Majority reads and writes force that intersection, but intersection alone is not linearisability.
```

With three replicas, `QUORUM` reads and writes each require two, so every read group intersects every successful write group. `ONE` reads and writes can use different replicas and miss an update. Overlap is necessary but not sufficient for linearisability: concurrent writes, last-write-wins timestamps and failed writes that partly landed still need extra machinery such as lightweight transactions.

> [!tip] The everyday question
> PACELC's "E" half is the one you face daily. Partitions are rare; latency is paid on every request. "Do we need this read to be strongly consistent, at the cost of a cross-zone round trip?" is a question you'll ask constantly.

## Key takeaways
- Describe each API’s guarantees rather than relying on a CP or AP label.
- Read and write replica counts exceeding the replication factor force overlap under the model’s assumptions.
- Overlap alone does not provide linearisability in the presence of concurrent or partly applied writes.
- ZooKeeper follower reads may lag committed writes; etcd’s default linearisable reads use a different contract.

## Further reading
- [Please stop calling databases CP or AP](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html)
- [Consistency Tradeoffs in Modern Distributed Database System Design](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
- [ZooKeeper consistency guarantees](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkGuarantees)
- [etcd API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/)
- [ZooKeeper sync quorum discussion](https://issues.apache.org/jira/browse/ZOOKEEPER-1675)
