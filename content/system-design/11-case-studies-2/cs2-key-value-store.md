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

Start with storage. Each key is kept on several nodes; the number of copies is the **replication factor** (RF). Assume 100 TB (terabytes) of logical data, meaning the data as the application sees it, and RF = 3:

```formula
D = L × RF
D = 100 TB × 3 = 300 TB
where
D: raw data stored across the whole cluster
L: logical data, one copy of everything; here 100 TB
RF: replication factor, the number of copies of each key; here 3
TB: terabytes, 10^12 bytes
In words: three copies of 100 TB is 300 TB on disk.
```

Each node has an 8 TB SSD (solid-state drive), but you keep about half free for SSTable compaction and headroom, so only about 4 TB is usable:

```formula
n = D / u
n = 300 TB / 4 TB = 75 nodes
where
n: the minimum number of nodes for capacity alone
D: raw data to store; 300 TB
u: usable space per node; 8 TB × 50% = 4 TB
TB: terabytes
nodes: servers in the cluster
In words: 300 TB at 4 TB a node needs at least 75 nodes; plan for about 100 to allow growth and losing a rack.
```

Now traffic. Assume 1 M (one million) operations a second, 70% reads. Every logical read asks 2 replicas (a read consistency level of 2) and every logical write is sent to all 3 replicas:

```formula
r = 700,000/s × 2 = 1,400,000/s
w = 300,000/s × 3 = 900,000/s
p = (r + w) / n
p = 2,300,000/s / 100 ≈ 23,000/s
where
r: replica reads per second (700,000 logical reads, each asking R = 2 replicas)
w: replica writes per second (300,000 logical writes, each sent to RF = 3 replicas)
p: replica operations per node per second
n: nodes in the cluster; here 100
s: seconds
≈: approximately equal to
In words: a million client operations become about 2.3 million replica operations, about 23,000 a second for each of 100 nodes.
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

Hash each key (Cassandra uses Murmur3) onto a ring of 2^64 tokens (64 copies of 2 multiplied together, about 1.8 × 10^19 possible positions). Each node owns positions on the ring, and a key belongs to the first node clockwise from its hash.

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

The rule that makes reads see writes is a simple counting argument. If a read asks R replicas and a write was confirmed by W replicas, and together they add up to more than the N replicas that exist, the two groups must share at least one replica:

```formula
R + W > N
2 + 2 > 3
where
R: replicas that must answer a read
W: replicas that must acknowledge a write
N: replicas that hold the key (the replication factor); typically 3
>: is greater than
In words: if read and write groups together are bigger than the number of copies, they must overlap in at least one replica.
```

With N = 3 and R = W = 2, any two replicas you read include at least one of the two that confirmed the write (2 + 2 = 4, but there are only 3 replicas). So if **R + W > N**, every read quorum overlaps every write quorum in at least one replica, so a read contacts at least one replica from each completed write quorum. Returning the latest real-time write additionally depends on version ordering and concurrency handling; overlap alone is not linearizability.

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

Suppose replica B for key k is down. A strict quorum fails only if too few home replicas respond: with 3 replicas and 2 acknowledgements required, one failed replica is tolerable. Dynamo instead uses a **sloppy quorum**: the write goes to the first N *healthy* nodes on the ring, so node D stands in for B. D stores the write with a **hint** saying "this belongs to B". When gossip shows B is back, D **hands off** the data and deletes its copy.

This keeps writes available during failures. The price is that R + W > N no longer guarantees overlap, because the W nodes that acknowledged may not be the "home" replicas that a later read asks.

Cassandra kept hinted handoff but not the sloppy quorum. A hint doesn't count towards the consistency level (except at the special `ANY` level), so a `QUORUM` write still needs acknowledgements from real home replicas, and fails if too few are up.

Hints are a short-term fix. Cassandra stops collecting hints for a node once it has been down longer than `max_hint_window` (3 hours by default). After a longer outage, only repair (below) brings that replica back in sync.

## Conflict resolution

Without a leader, two clients can update the same key concurrently on different replicas. When the versions meet, which one wins?

### Vector clocks (Dynamo, Riak)
Each version carries a vector of `(node, counter)` pairs.

- If one vector is ≥ (greater than or equal to) the other in every entry and strictly greater in at least one, it **descends** from it, and the older version can be discarded:

```formula
a_x ≥ b_x  ∀ x
a_x > b_x  ∃ x
where
a: one version's vector clock
b: the other version's vector clock
a_x: the counter for node x in clock a (0 if x is missing)
b_x: the counter for node x in clock b (0 if x is missing)
x: a node name that appears in either clock
≥: is greater than or equal to
>: is strictly greater than
∀: "for every": the line must hold for all nodes x
∃: "for at least one": the line must hold for some node x
In words: version a descends from version b when every node's counter in a is at least as big as in b, and at least one is bigger.
```

For example, a = {A: 3, B: 1} descends from b = {A: 2, B: 1}, because 3 ≥ 2 and 1 ≥ 1 with 3 > 2.
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

- **Hot keys**: one key's load lands on its N replicas (typically 3), however many nodes you have. Mitigate with client-side caching, or by splitting the key into sub-keys.
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
