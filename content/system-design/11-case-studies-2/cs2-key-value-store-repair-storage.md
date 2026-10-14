---
id: cs2-key-value-store-repair-storage
title: Repair, tombstones and LSM storage
level: advanced
minutes: 4
summary: Maintain replicas and select compaction around the lifetime of data and deletes.
sourceLesson: cs2-key-value-store
---

## Permanent failures: anti-entropy with Merkle trees

Hinted handoff covers short outages. After longer ones, or lost hints, replicas drift apart. Two mechanisms repair them:

- **Read repair**: Cassandra detects divergent responses and, with blocking read repair enabled, repairs stale replicas involved in that read. The table can instead select read_repair NONE; a read does not necessarily repair every replica or row.
- **Anti-entropy repair**: replicas construct or maintain **Merkle trees** over key ranges (leaves are hashes of key ranges, parents are hashes of their children). Two replicas compare root hashes. Matching hashes are evidence of matching represented content, subject to correct construction and negligible collision risk. If not, they recurse only into the differing subtrees, so they find the divergent keys while exchanging very little data. In Cassandra this is `nodetool repair`, which should run regularly (see the tombstones section below).

## Membership and failure detection: gossip

There's no central coordinator. Each node, about once a second, **gossips** with a random peer, exchanging versioned state such as heartbeats, tokens and status. Information spreads epidemically, typically spreading in O(log N) rounds, where N is the number of nodes and O(log N) means the rounds grow with the logarithm of N (doubling the cluster adds only about one more round), under an idealised connected random-gossip model, not a worst-case deadline.

- **Seed nodes** give new nodes a first contact and keep the cluster from splitting into islands.
- Failure detection is **local and probabilistic**. Cassandra uses the **phi accrual failure detector**, which outputs a suspicion level based on how late heartbeats are compared with their history, instead of a fixed timeout.
- Membership changes (joining, leaving) are explicit admin actions, gossiped around the cluster. Transient unavailability is handled by hints, not by moving ranges.

## Storage engine: LSM trees and compaction

Each node uses a **log-structured merge tree**, optimised for heavy writes:

```
write -> commit log (append; sync policy)
      -> memtable (sorted, in RAM)
      -> flush when full -> SSTable
         (immutable, sorted file)
read  -> memtable, then SSTables
         newest -> oldest, using
         Bloom filter + index per SSTable
```

- Commit-log writes are append-oriented. Cassandra 5.0 defaults to periodic sync, which can acknowledge before fsync; batch/group modes wait for log flush. Durability and latency depend on this choice and replication.
- Reads may touch several SSTables. **Bloom filters** skip SSTables that definitely don't contain the key.
- **SSTable compaction** merges SSTables, drops overwritten values and expired data, and bounds read amplification:

These are three classic workload-specific strategies, rather than an exhaustive list of current options. Cassandra 5.0 also offers Unified Compaction Strategy; evaluate the deployed release and workload.

| Strategy | Best for |
|---|---|
| Size-tiered (STCS) | write-heavy, general |
| Leveled (LCS) | read-heavy, many updates |
| Time-window (TWCS) | time series with TTL |

STCS has low write amplification but high space amplification (it needs headroom). LCS limits overlap within each nonzero level for point lookups but rewrites data more often. The fraction of reads satisfied by one SSTable depends on the workload and data distribution. TWCS groups data by time window so whole expired SSTables can be dropped.

### Deletes and tombstones
You can't delete from immutable SSTables, so a delete writes a **tombstone**. It must outlive every replica's copy of the old value. Otherwise a replica that missed the delete would "resurrect" the data during repair. Cassandra normally retains tombstones for at least `gc_grace_seconds` (default 10 days); removing them also requires compaction safety conditions. Complete repair across relevant replicas before deletion markers can be removed. An overdue stale replica needs a safe recovery/rebuild procedure, not blind rejoining. Workloads that delete heavily also make reads scan many tombstones, a common performance problem.

## Key takeaways
- Merkle comparison locates represented differences with hash-collision assumptions.
- Commit-log synchronization mode affects the acknowledgement durability contract.
- Repair stale replicas safely before deletion metadata can be purged.

## Further reading
- [Dynamo: Amazon's highly available key-value store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Dynamo architecture (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Compaction (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/index.html)
- [Merkle tree (Wikipedia)](https://en.wikipedia.org/wiki/Merkle_tree)
- [Log-structured merge-tree (Wikipedia)](https://en.wikipedia.org/wiki/Log-structured_merge-tree)
- [Unified Compaction Strategy](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/ucs.html)
