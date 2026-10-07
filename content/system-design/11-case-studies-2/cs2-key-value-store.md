---
id: cs2-key-value-store
title: Distributed key-value store (Dynamo / Cassandra)
level: advanced
minutes: 19
summary: Design a leaderless, availability-oriented key-value store, covering consistent hashing with virtual nodes, quorum replication, sloppy quorums and hinted handoff, vector clocks versus last-write-wins, gossip, Merkle-tree repair and LSM compaction.
---

The 2007 Amazon Dynamo paper is one of the most influential papers in distributed systems. Amazon needed a store where "add to basket" remains available through many node and network failures, subject to reachable replicas and capacity. The answer was a **leaderless**, **eventually consistent** key-value store that combines about a dozen techniques. Cassandra, Riak and ScyllaDB all follow its design.

(Note that Amazon's *DynamoDB* service is a different design: its 2022 architecture paper describes leader-based Multi-Paxos replication per partition.)

This case study is a tour of those techniques, and why each one is needed.

## Requirements

### Functional
- `put(key, value, context)` and `get(key) -> (value(s), context)`.
- Values are opaque blobs, usually under 1 MB.
- Optional TTL per key.

### Non-functional
- **Availability-oriented**: accept writes where enough suitable nodes remain reachable; chosen quorum levels can sacrifice availability during partitions.
- **Tunable consistency** per request: from "fast, maybe stale" to "read your writes".
- **Predictable tail latency**: the Dynamo paper framed SLAs at the 99.9th percentile, not the average.
- **Incremental scalability**: add a node and it takes a fair share of the data, with no big-bang resharding.
- **No single point of failure**: every node is equal (symmetric, decentralised).

## Back-of-the-envelope

```
Data: 100 TB logical, RF = 3 -> 300 TB
Node: 8 TB SSD, keep ~50% free for
  compaction + headroom -> 4 TB usable
Nodes: 300 / 4 = 75 -> ~100 with
  room to grow / lose a rack
Traffic: 1 M ops/s (70% reads)
  Reads at R=2: 700 k x 2
    = 1.4 M replica reads/s
  Writes at RF 3: 300 k x 3
    = 900 k replica writes/s
  Per node: ~2.3 M / 100 = ~23 k ops/s
```

What matters:

- The 23k/node estimate counts logical replica operations, not equal-cost disk I/Os. Payloads, digests, compaction, caching and skew determine actual capacity; benchmark rather than assuming NVMe makes it comfortable.

> **Content gap:** no reproducible throughput benchmark or universal partition-size threshold is supplied. Storage and traffic figures are scenario assumptions. Product details below describe the cited Cassandra 5.0 documentation and historical Dynamo/DynamoDB papers, not every future release.
- **Headroom for compaction** is a real sizing factor. Size-tiered compaction can temporarily need as much free space again as the data being compacted.
- At 100 nodes, plan for routine failures rather than assuming a failure-free fleet. Failure handling is normal operation, not an edge case.

## API design

```
GET  /kv/{key}?consistency=QUORUM
  -> 200 { values: [v1, v2?],
           context: "<vector clock>" }
PUT  /kv/{key}?consistency=QUORUM
  { value, context, ttl_s? }
DELETE /kv/{key}  { context }
```

The `context` is the version information the client read (a vector clock). Passing it back on `put` tells the store which versions this write **supersedes**. That's how it tells "an update" apart from "a concurrent conflicting write".

## Partitioning: consistent hashing with virtual nodes

Hash each key (Cassandra uses Murmur3) onto a ring of 2^64 tokens. Each node owns positions on the ring, and a key belongs to the first node clockwise from its hash.

```
        ring (hash space)
           A1
       C2      B1
     B3          A2
       A3      C1
           B2
 key k -> hash -> walk clockwise
 -> first 3 distinct nodes = replicas
```

With one token per node, load is lumpy, and when a node leaves, its whole range lands on its single successor. **Virtual nodes** (many tokens per physical node) fix both problems. Each node owns many small ranges, load evens out statistically, and a failed node's load spreads across many peers. The cited Cassandra 5.0 configuration ships `num_tokens:16`, compared with the older 256-token default, because fewer vnodes make repair and streaming cheaper. To keep balance good with so few tokens, it also enables a token-allocation algorithm (`allocate_tokens_for_local_replication_factor: 3`) instead of choosing tokens purely at random.

The **preference list** for a key is the next N *distinct physical* nodes clockwise, skipping vnodes on the same machine and, ideally, choosing different racks or availability zones.

## Replication and quorums

Each key is stored on **N** replicas (typically 3). Any node can act as **coordinator** for a request. It forwards to the replicas and waits for:

- **W** acknowledgements for a write,
- **R** responses for a read.

If **R + W > N**, every read quorum overlaps every write quorum in at least one replica, so a read contacts at least one replica from each completed write quorum. Returning the latest real-time write additionally depends on version ordering and concurrency handling; overlap alone is not linearizability.

| Setting (N=3) | Behaviour |
|---|---|
| W=1, R=1 | fastest, may read stale |
| W=2, R=2 | overlap, the classic Dynamo choice |
| W=3, R=1 | fast reads, writes fail if any replica is down |
| W=1, R=3 | fast writes, slow, fragile reads |

For writes, the coordinator sends to all N replicas and returns as soon as the fastest W reply. Dynamo did the same for reads, asking all N and returning after R. Cassandra reads contact only as many replicas as the consistency level needs (one full read plus digests from the others), and uses **speculative retry** to ask another replica if one is slow. Waiting for fewer than all replicas or successful speculative reads can reduce tail latency; ALL still waits for every required replica.

Cassandra names these levels `ONE`, `QUORUM` and `ALL`, plus `LOCAL_QUORUM` for multi-data-centre setups. Driver defaults vary by driver and version. Configure the consistency level explicitly when the application requires overlapping quorums.

> [!warning] Quorums aren't linearisability
> Even with R + W > N, edge cases exist: a write that fails at the coordinator but succeeded on some replicas, concurrent reads during a write, sloppy quorums, and last-write-wins clock skew. Quorum overlap alone is insufficient for linearizability; suitably designed quorum protocols can provide it. The basic Dynamo/LWW operations described here do not automatically do so. Cassandra offers lightweight transactions (Paxos) for compare-and-set when you really need it, at the cost of several extra round trips.

## Handling temporary failures: sloppy quorum and hinted handoff

Suppose replica B for key k is down. A strict quorum fails only if too few home replicas respond: withN=3,W=2, one failed replica is tolerable. Dynamo instead uses a **sloppy quorum**: the write goes to the first N *healthy* nodes on the ring, so node D stands in for B. D stores the write with a **hint** saying "this belongs to B". When gossip shows B is back, D **hands off** the data and deletes its copy.

This keeps writes available during failures. The price is that R + W > N no longer guarantees overlap, because the W nodes that acknowledged may not be the "home" replicas that a later read asks.

Cassandra kept hinted handoff but not the sloppy quorum. A hint doesn't count towards the consistency level (except at the special `ANY` level), so a `QUORUM` write still needs acknowledgements from real home replicas, and fails if too few are up.

Hints are a short-term fix. Cassandra stops collecting hints for a node once it has been down longer than `max_hint_window` (3 hours by default). After a longer outage, only repair (below) brings that replica back in sync.

## Conflict resolution

Without a leader, two clients can update the same key concurrently on different replicas. When the versions meet, which one wins?

### Vector clocks (Dynamo, Riak)
Each version carries a vector of `(node, counter)` pairs.

- If one vector is ≥ the other in every entry and strictly greater in at least one, it **descends** from it, and the older version can be discarded.
- If neither dominates, the writes were **concurrent**. Both versions (siblings) are kept and returned to the client on read, and the **application merges** them, then writes the result with the merged context.

Amazon's shopping basket merged siblings by **union**. Nothing added is ever lost, but a deleted item can occasionally reappear, which the paper accepts as the business trade-off. To stop vector clocks growing without limit, Dynamo truncated the oldest entries beyond about 10, accepting possible loss of causal precision; the paper gives 10 as an example threshold, not a universal setting.

### Last-write-wins (Cassandra)
Each *cell* (column value) carries a write timestamp, and the highest timestamp wins. It's simple, needs no siblings and makes reads cheap. But **concurrent writes are silently lost**, and **clock skew** can make an older write win. If node clocks drift by 200 ms, a write made 100 ms later can lose. Run NTP carefully, model data to avoid concurrent read-modify-write cycles (use per-element columns, counters or collections), or use lightweight transactions.

### CRDTs
Riak added CRDT data types (counters, sets, maps) that converge under their specified merge semantics, which is the best of both worlds for suitable data.

## Permanent failures: anti-entropy with Merkle trees

Hinted handoff covers short outages. After longer ones, or lost hints, replicas drift apart. Two mechanisms repair them:

- **Read repair**: when a quorum read sees divergent versions, the coordinator writes the newest version back to the stale replicas.
- **Anti-entropy repair**: replicas construct or maintain **Merkle trees** over key ranges (leaves are hashes of key ranges, parents are hashes of their children). Two replicas compare root hashes. Matching hashes are evidence of matching represented content, subject to correct construction and negligible collision risk. If not, they recurse only into the differing subtrees, so they find the divergent keys while exchanging very little data. In Cassandra this is `nodetool repair`, which should run regularly (see the tombstones section below).

## Membership and failure detection: gossip

There's no central coordinator. Each node, about once a second, **gossips** with a random peer, exchanging versioned state such as heartbeats, tokens and status. Information spreads epidemically, typically spreading in O(log N) rounds under an idealized connected random-gossip model, not a worst-case deadline.

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
- **Compaction** merges SSTables, drops overwritten values and expired data, and bounds read amplification:

| Strategy | Best for |
|---|---|
| Size-tiered (STCS) | write-heavy, general |
| Leveled (LCS) | read-heavy, many updates |
| Time-window (TWCS) | time series with TTL |

STCS has low write amplification but high space amplification (it needs headroom). LCS limits overlap within each nonzero level for point lookups but rewrites data more often. The fraction of reads satisfied by one SSTable depends on the workload and data distribution. TWCS groups data by time window so whole expired SSTables can be dropped.

### Deletes and tombstones
You can't delete from immutable SSTables, so a delete writes a **tombstone**. It must outlive every replica's copy of the old value. Otherwise a replica that missed the delete would "resurrect" the data during repair. Cassandra normally retains tombstones for at least `gc_grace_seconds` (default 10 days); purge also requires compaction safety conditions. Complete repair across relevant replicas before tombstones can be purged. An overdue stale replica needs a safe recovery/rebuild procedure, not blind rejoining. Workloads that delete heavily also make reads scan many tombstones, a common performance problem.

## High-level architecture

```
        client (or smart driver)
                 |
                 v
     +-----------------------+
     | any node: coordinator |
     +-----------------------+
       /         |         \
      v          v          v
 +---------+ +---------+ +---------+
 |replica A| |replica B| |replica C|
 |commitlog| |commitlog| |commitlog|
 |memtable | |memtable | |memtable |
 |SSTables | |SSTables | |SSTables |
 +---------+ +---------+ +---------+
   ^   gossip, hints, Merkle repair  ^
   +---------------------------------+
```

Token-aware client drivers send each request straight to a replica for the key, saving a network hop.

## Bottlenecks and trade-offs

- **Hot keys**: one key's load lands on N nodes, however many nodes you have. Mitigate with client-side caching, or by splitting the key into sub-keys.
- **Large partitions** (in Cassandra's wide-row model): oversized partitions can hurt compaction, repair and memory use; no universal 100MB cliff applies. Bucket by time or hash to keep partitions small.
- **LWW vs vector clocks**: LWW is simpler but loses concurrent writes. Vector clocks expose concurrency but push merge correctness onto applications; truncation can lose causal information.
- **Repair cost**: Merkle repair is I/O heavy. Incremental repair, or tools such as Cassandra Reaper, schedule it in small slices.
- **Consistency choice is per request**, so teams must actually understand R, W and N.

## Evolving at 10x

- **1 PB, 1,000 nodes**: vnodes let new nodes stream small ranges from many peers in parallel. Limit concurrent streaming so bootstrapping doesn't hurt foreground latency.
- **Multiple regions**: replicate per data centre (`NetworkTopologyStrategy`, for example 3 replicas in each of 2 regions), and use `LOCAL_QUORUM` for latency, with asynchronous cross-region replication.
- **Stronger guarantees** where needed: Paxos-based lightweight transactions for compare-and-set (classic Cassandra Paxos takes four round trips, and newer versions cut that), or move those entities to a consensus-based store. Check the deployed Cassandra release for available transaction protocols; the historical DynamoDB paper provides a separate example of leader-based partitions.
- **Operational automation**: scheduled repair, node replacement, compaction tuning and capacity forecasting become a platform team's main job.

## Key takeaways
- Consistent hashing with virtual nodes gives even load and incremental scaling. A key's replicas are the next N distinct physical nodes, spread across racks or AZs.
- Leaderless replication with tunable R and W: R + W > N gives overlapping quorums, while waiting for only the fastest replicas protects tail latency. Quorums still aren't linearisable.
- Sloppy quorums plus hinted handoff keep writes available through failures. Read repair and Merkle-tree anti-entropy fix longer-lived divergence.
- Conflicts are resolved by vector clocks plus application merges (Dynamo), last-write-wins on timestamps (Cassandra, which is sensitive to clock skew), or CRDTs.
- The node-level engine is an LSM tree: commit log, memtable, SSTables, Bloom filters, and a compaction strategy chosen to suit the workload. Tombstones must outlive the repair interval (gc_grace) or deleted data comes back.

## Further reading
- [Dynamo: Amazon's highly available key-value store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Amazon's Dynamo (Werner Vogels)](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html)
- [Dynamo architecture (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Compaction (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/index.html)
- [Consistent hashing (Wikipedia)](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Vector clock (Wikipedia)](https://en.wikipedia.org/wiki/Vector_clock)
- [Merkle tree (Wikipedia)](https://en.wikipedia.org/wiki/Merkle_tree)
- [Log-structured merge-tree (Wikipedia)](https://en.wikipedia.org/wiki/Log-structured_merge-tree)
