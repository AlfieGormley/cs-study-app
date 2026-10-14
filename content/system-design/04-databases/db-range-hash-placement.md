---
id: db-range-hash-placement
title: Range and hash partition placement
level: advanced
minutes: 5
summary: Compare ordered-key locality with hash distribution and calculate why changing modulo placement moves most keys.
sourceLesson: db-partitioning
---

Replication gives you copies of the same data. **Partitioning** splits data into subsets; **sharding** distributes them among nodes. Systems use different physical units: MongoDB chunks/shards, Elasticsearch shards, HBase regions and Bigtable tablets. Cassandra virtual nodes own token ranges and are not the same thing as CQL partitions. You partition when one machine can't hold the data or absorb the write rate.

The goal is to spread data *and load* evenly. A partition that gets far more than its share is a **hot spot**, and it caps the throughput of the entire system.

In practice, each partition is also replicated, so a node holds replicas of several partitions:

```
        P1      P2      P3
Node A: lead    foll    -
Node B: foll    lead    foll
Node C: -       foll    lead
```

## Range partitioning

Assign contiguous ranges of the key to each partition, like volumes of an encyclopaedia: A–C, D–F, and so on.

```
 key range        partition
 [a ... f)    ──►   P1
 [f ... m)    ──►   P2
 [m ... t)    ──►   P3
 [t ... ∞)    ──►   P4
```

- **Pro**: range scans are efficient. "All events between 09:00 and 10:00" touches the partitions overlapping that range; the number depends on boundaries and data volume.
- **Con**: hot spots when writes cluster in one range. If the key is a timestamp, *all* of today's writes go to the last partition while the others sit idle.
- Boundaries are usually chosen automatically, splitting a partition when it grows too big according to engine-specific policies and thresholds; verify these for the deployed version.

Fix for time-ordered hot spots: prefix the key with something that spreads load, e.g. `sensor_id + timestamp`, so writes from different sensors land in different ranges. Range queries then need one query per sensor.

## Hash partitioning

Apply a hash function to the key and assign ranges of the *hash* to partitions. A good hash spreads even sequential keys uniformly.

The naive way to turn a hash into a partition number is to take the remainder after dividing by the number of partitions:

```formula
p = hash(key) mod N
where
p: the partition (or node) number the key is sent to, from 0 to N − 1
hash: a hash function, which turns any key into a large, evenly spread number; the same key always gives the same number
key: the record's partition key, e.g. a user id
mod: modulo, the remainder after whole-number division (17 mod 5 = 2)
N: the number of partitions or nodes
In words: hash the key, divide by the number of partitions, and the remainder says where the key lives.
```

For example, if `hash("user42")` came out as 1,000,003 and N = 10, the remainder is 3, so the key goes to partition 3. This spreads keys evenly, but it has a fatal flaw when N changes, described in the warning below.

- **Pro**: even distribution, no clustering.
- **Con**: range queries on the key are gone: adjacent keys are scattered. Cassandra's compromise is a *compound* key: hash the partition key, then keep rows sorted by the clustering columns within each partition.

> [!warning] Never use hash mod N directly
> Going from 10 to 11 nodes, a key stays put only if its hash leaves the same remainder when divided by 10 and by 11, which is true for about 1 in 11 keys. Adding one node moves ~91% of the data.

The general rule, for hash values spread evenly, when you add one node to N:

```formula
F_stay = 1 / (N + 1)
F_move = 1 − 1 / (N + 1)
where
F_stay: the fraction of keys whose partition number stays the same
F_move: the fraction of keys that must move to a different node
N: the number of nodes before you add one
In words: with modulo placement, adding one node keeps only about one key in N + 1 where it was; almost everything moves.
```

For 10 nodes growing to 11:

```formula
F_stay = 1 / (10 + 1) ≈ 0.09
F_move ≈ 1 − 0.09 = 0.91
where
F_stay: the fraction of keys that stay, about 9%
F_move: the fraction of keys that move, about 91%
≈: approximately equal to
In words: adding an eleventh node moves about 91% of the data, when ideally it would move only the new node's share, about 9%.
```

Why 1 in N + 1: a key stays only when its two remainders match, and over every run of N × (N + 1) consecutive hash values that happens for exactly N of them (the values 0 to N − 1 and their repeats).

## Key takeaways
- Sharding spreads both data and load; replication supplies copies of each partition.
- Range keys preserve range locality but concentrate monotonically increasing writes.
- Hashing spreads keys, but plain modulo placement remaps most keys when one node is added.

## Further reading
- [DynamoDB: Designing partition keys to distribute your workload](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html)
- [DeCandia et al.: Dynamo, Amazon's highly available key-value store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
