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

In a leaderless store like Cassandra, each key is copied to several replicas. A write is reported successful once some of them acknowledge it, and a read asks some of them and takes the newest answer. A read is guaranteed to include at least one replica holding the latest successful write when the two groups must overlap:

```formula
W + R > N
Q = ⌊N / 2⌋ + 1
N = 3: Q = ⌊1.5⌋ + 1 = 2
W = R = 2: 2 + 2 = 4 > 3
W = R = 1: 1 + 1 = 2 < 3
where
N: the replication factor, the number of replicas holding each key
W: the number of replicas that must acknowledge a write before it counts as successful
R: the number of replicas a read consults
Q: the size of a majority quorum, what Cassandra's QUORUM level uses
⌊ ⌋: floor: round down to the whole number below (1.5 becomes 1)
>: is greater than
<: is less than
In words: if the replicas you write to plus the replicas you read from add up to more than the total, the two groups must share at least one replica, so the read sees the write.
```

With three replicas, `ONE` reads and `ONE` writes each involve one replica. Their combined count is two, below three, so the groups can be disjoint and a read can miss the latest write. Overlap is necessary but not sufficient for linearisability: concurrent writes, last-write-wins timestamps and failed writes that partly landed still need extra machinery such as lightweight transactions.

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
