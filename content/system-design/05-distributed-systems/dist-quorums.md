---
id: dist-quorums
title: Quorums and Dynamo-style replication
level: intermediate
minutes: 13
summary: N, R and W; why R + W > N isn't the whole story; sloppy quorums, hinted handoff, read repair and Merkle-tree anti-entropy.
---

Leader-based replication (covered in the databases module) sends every write through one node. Amazon's 2007 Dynamo paper popularised the alternative: **leaderless replication**, where clients (or a coordinator acting for them) send each write to several replicas in parallel and consider it done once enough of them acknowledge.

Cassandra, Riak, ScyllaDB and Voldemort all descend from this design. (DynamoDB the service, confusingly, uses leaders and Paxos internally.)

## N, R and W

Three numbers define a quorum system:

- **N**: how many replicas store each key (the replication factor).
- **W**: how many must acknowledge a write before it's reported successful.
- **R**: how many must respond to a read.

Keys are placed on a consistent-hash ring; the N replicas for a key are the next N distinct nodes clockwise (its **preference list**).

```
        A
     F     B     key k hashes here
               <- replicas: B, C, D
     E     C        (N = 3)
        D
```

### The overlap rule

If **R + W > N**, every read set overlaps every write set in at least one node, so a read contacts at least one replica holding the latest acknowledged write.

```
N=3, W=2, R=2:
write -> [B] [C]  .
read  ->  .  [C] [D]
overlap:     C
```

The read returns several versions; the client picks the newest by version (vector clock or timestamp).

There is a second overlap condition people forget. **W > N/2** means any two *write* sets overlap, so two writes can't both complete on disjoint replicas without at least one node seeing both. R + W > N alone doesn't give you that: with N = 5, W = 2, R = 4, reads overlap every write, but two concurrent writes can land on {A, B} and {C, D} and never meet. Then only the version-ordering rule (often a timestamp) decides which one survives.

| Config | Behaviour |
|---|---|
| N=3, W=2, R=2 | Balanced, tolerates 1 down |
| N=3, W=3, R=1 | Fast reads, writes need all |
| N=3, W=1, R=3 | Fast writes, reads need all |
| N=3, W=1, R=1 | Fast, no overlap, stale reads |

Fault tolerance: writes succeed with up to N − W replicas down; reads with up to N − R down. With N=3, W=2, R=2 you tolerate one failure for both.

Cassandra's `QUORUM` is ⌊N/2⌋ + 1 (2 of 3), where N is the total replication factor across all data centres. `LOCAL_QUORUM` counts only replicas in the coordinator's data centre, avoiding cross-region latency, but it also means the overlap guarantee only holds for reads and writes made in the **same** data centre.

## Why R + W > N is not linearizable

It's tempting to think overlap gives strong consistency. It doesn't, for several reasons:

1. **Concurrent writes**: two clients write different values; replicas may observe different orders. Concurrent writes have no intrinsic real-time winner; a timestamp policy chooses one, and skew can also misorder writes that are not concurrent.
2. **A write in progress**: if a write has reached 1 of 3 replicas, one reader might see it and a later reader might not. That's a linearizability violation (new value, then old).
3. **Timed-out writes have unknown outcomes**: if W=2 but only 1 replica acked, the write may later spread. That alone is allowed by linearisability; a later new-then-old read sequence or a definitive abort followed by application would violate the relevant contract.
4. **Sloppy quorums** (below) break the overlap entirely.
5. A replica holding the new value **fails and is restored** from an older replica, dropping below W copies.

```
W=3 write of x=1 in progress:
B: x=1   C: x=0   D: x=0
read 1 (B,C)  -> sees 1
read 2 (C,D)  -> sees 0   new then old!
```

You *can* make a quorum register linearizable, but it takes more than R + W > N. The ABD algorithm (Attiya, Bar-Noy and Dolev) needs:

1. **Strict quorums**: no sloppy stand-ins.
2. **Readers write back**: before returning, the reader writes the newest value it saw to a write quorum, so no later reader can see anything older (this fixes case 2).
3. **Writers read first** (with several writers): a writer first asks a quorum for the highest version, then writes with a strictly higher one, so versions follow real-time order rather than skewed clocks (this fixes case 1).

That gives linearizable reads and writes of single registers. It still doesn't give compare-and-set or other read-modify-write operations, which need consensus. Cassandra's blocking read repair gives you something like step 2 (monotonic quorum reads), but its writes use client or coordinator timestamps, so step 3 is missing.

> [!note] Quorums give probabilistic freshness
> Peter Bailis's Probabilistically Bounded Staleness (PBS) work modelled real production latency profiles (from LinkedIn and Yammer) and found that even partial quorums such as N=3, R=W=1 usually returned the latest value within milliseconds to tens of milliseconds of a write. Eventual isn't usually long, but it isn't bounded either.

## Sloppy quorums and hinted handoff

Strict quorums lose availability when replicas are unreachable. If B and C are down, a W=2 write to key k fails, even though most of the cluster is healthy.

A **sloppy quorum** accepts the write on the next healthy nodes on the ring, outside the preference list:

```
pref list: B, C, D  (B, C down)
write W=2 -> D  and  E (stand-in)
E stores it with a hint: "for B"
```

When B comes back, E's **hinted handoff** process delivers the write to B and deletes its copy.

Trade-off: sloppy quorums boost write availability, but R + W > N no longer guarantees overlap, because the W nodes may not be among the N that a reader asks. Until handoff completes, a read from B, C, D can miss the write. Riak uses sloppy quorums by default (its `PR` and `PW` settings can require that a number of true, "primary" replicas respond); Cassandra stores hints (for up to 3 hours by default, `max_hint_window`) but still counts only true replicas towards the consistency level, except at `ANY`.

If a replica is down for longer than the hint window, hints stop being stored for it, and only repair (below) will bring it back up to date.

## Read repair

When a read with R > 1 gets differing versions, the coordinator knows some replicas are stale. **Read repair** writes the newest version back to them.

```
read R=3:
B: v5  C: v5  D: v3
return v5; send v5 -> D
```

This only fixes keys that are read. Rarely read keys can stay stale indefinitely, so you also need background repair.

## Anti-entropy with Merkle trees

Anti-entropy compares replicas in the background and copies missing data. Comparing every key over the network would be enormous, so Dynamo uses **Merkle trees** (hash trees).

Each replica builds a tree over a key range. Leaves hash small sub-ranges of keys; each parent hashes its children.

```
          root
        /      \
     h12        h34
    /   \      /   \
  h1    h2   h3    h4
 keys  keys keys  keys
 0-24 25-49 50-74 75-99
```

Two replicas compare roots. If they're equal, the range is identical: done in one hash comparison. If not, compare the children and recurse only into subtrees that differ.

> [!example] How much does it save?
> 1 billion keys, leaves of ~1,000 keys, so ~1 million leaves and a tree depth of 20. If one key differs, replicas exchange about 2 hashes per level × 20 levels = 40 hashes, then sync one leaf range of 1,000 keys, instead of comparing a billion.

Costs: trees must be rebuilt or updated when data changes, and recalculated when nodes join or leave (key ranges shift). Cassandra's `nodetool repair` builds Merkle trees per token range; operators must run it at least every `gc_grace_seconds` (10 days by default), otherwise deleted data can be **resurrected** when a replica that missed a tombstone reintroduces the old value after the tombstone is purged.

## Putting it together

| Mechanism | Fixes | When |
|---|---|---|
| Hinted handoff | Writes missed by down nodes | On recovery |
| Read repair | Stale replicas of hot keys | On read |
| Anti-entropy | Everything else | Background |

## Key takeaways
- N replicas per key; a write needs W acks, a read needs R responses. R + W > N makes read and write sets overlap.
- Overlap is not linearizability: concurrent writes, in-flight writes, unrolled failed writes and sloppy quorums all leak stale reads.
- W > N/2 makes write sets overlap too; linearizable quorum registers (ABD) also need readers to write back and writers to read versions first.
- Tolerance is N − W failures for writes and N − R for reads.
- Sloppy quorums keep writes available during failures by using stand-in nodes, with hinted handoff to deliver later, at the cost of overlap.
- Read repair fixes stale replicas on the read path; Merkle-tree anti-entropy skips matching subtrees; one differing leaf needs logarithmic tree descent, but many differences can require scanning much of the tree.
- In Cassandra, run repair within gc_grace_seconds or deleted data can come back.

## Further reading
- [Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Cassandra Dynamo architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Cassandra repair](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/repair.html)
- [Cassandra hints](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/hints.html)
- [Probabilistically Bounded Staleness (VLDB 2012)](https://www.vldb.org/pvldb/vol5/p776_peterbailis_vldb2012.pdf)
- [Merkle tree (Wikipedia)](https://en.wikipedia.org/wiki/Merkle_tree)
- [Quorum (distributed computing) (Wikipedia)](https://en.wikipedia.org/wiki/Quorum_%28distributed_computing%29)
