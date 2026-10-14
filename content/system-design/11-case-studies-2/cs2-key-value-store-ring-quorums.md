---
id: cs2-key-value-store-ring-quorums
title: Virtual nodes and overlapping quorums
level: advanced
minutes: 5
summary: Route to distinct replicas and understand the exact guarantee of quorum overlap.
sourceLesson: cs2-key-value-store
---

## API design

This is an illustrative endpoint contract, not a runnable HTTP request. Arrows distinguish responses from submitted fields.

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

Hash each key (Cassandra uses Murmur3) onto the 64-bit token space. Its size is:

```formula
H = 2^64 ≈ 1.84 × 10^19
where
H: number of possible 64-bit hash positions, a count
≈: approximately equal after rounding
In words: A 64-bit hash space contains about eighteen quintillion possible positions.
```

 Each node owns positions on the ring, and a key belongs to the first node clockwise from its hash.

```diagram
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

The rule establishing replica-set overlap is a simple counting argument. If a read asks R replicas and a write was confirmed by W replicas, and together they add up to more than the N replicas that exist, the two groups must share at least one replica:

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

With three replicas and two required acknowledgements for each read and write, every selected read pair includes at least one member of every confirmed write pair. Returning the latest real-time write additionally depends on version ordering and concurrency handling; overlap alone is not linearizability.

| Required read/write counts, 3 replicas | Behaviour |
|---|---|
| 1 write, 1 read | fastest, may read stale |
| 2 writes, 2 reads | overlap, the classic Dynamo choice |
| 3 writes, 1 read | fast reads, writes fail if any replica is down |
| 1 write, 3 reads | fast writes, slow, fragile reads |

For writes, the coordinator sends to all N replicas and returns as soon as the fastest W reply. Dynamo did the same for reads, asking all N and returning after R. Cassandra reads contact only as many replicas as the consistency level needs (one full read plus digests from the others), and uses **speculative retry** to ask another replica if one is slow. Waiting for fewer than all replicas or successful speculative reads can reduce tail latency; ALL still waits for every required replica.

Cassandra names these levels `ONE`, `QUORUM` and `ALL`, plus `LOCAL_QUORUM` for multi-data-centre setups. Driver defaults vary by driver and version. Configure the consistency level explicitly when the application requires overlapping quorums.

> [!warning] Quorums aren't linearisability
> Even with overlapping read and write groups, edge cases exist: a write that fails at the coordinator but succeeded on some replicas, concurrent reads during a write, sloppy quorums, and last-write-wins clock skew. Quorum overlap alone is insufficient for linearizability; suitably designed quorum protocols can provide it. The basic Dynamo/LWW operations described here do not automatically do so. Cassandra offers lightweight transactions (Paxos) for compare-and-set when you really need it, at the cost of several extra round trips.

## Key takeaways
- Virtual tokens spread ranges among physical nodes and reduce skew statistically.
- Read and write counts exceeding the replica count force intersection.
- Overlap alone is insufficient for linearisability under failures, concurrent writes or clock-based ordering.

## Further reading
- [Dynamo: Amazon's highly available key-value store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Dynamo architecture (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Consistent hashing (Wikipedia)](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Cassandra 5.0 shipped configuration](https://raw.githubusercontent.com/apache/cassandra/cassandra-5.0/conf/cassandra.yaml)
