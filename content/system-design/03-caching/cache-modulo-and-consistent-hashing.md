---
id: cache-modulo-and-consistent-hashing
title: Compare modulo routing with consistent hashing
level: advanced
minutes: 4
summary: Calculate key movement when adding a node and explain how virtual nodes spread ownership and failures.
sourceLesson: cache-distributed
---

A partitioning rule maps each key to a cache server. Changes to that rule can turn a routine capacity increase into a sudden wave of misses.

## Partitioning

### The naive approach: hash mod N

The simplest way to pick a node is to turn the key into a number with a hash function and take the remainder after dividing by the number of nodes: `hash(key) % N` in code. A key whose hash is 1,000,003 goes to node 3 in a four-node cluster.

This spreads keys evenly, but it falls apart when N changes. Every key's node is recomputed from the new N, and a key stays put only if dividing its hash by the old and new node counts happens to leave the same remainder. Going from 4 to 5 nodes, that is true for only about 1 key in 5, so about **80%** of keys suddenly live on a different node, all of them missing at once. Bigger clusters are worse: growing from N to N + 1 nodes keeps only about 1 key in N + 1 in place. For a cache, that is a self-inflicted stampede on the database.

### Consistent hashing

Map both nodes and keys onto a ring (for example, a 32-bit hash space with 4,294,967,296 possible positions). A key belongs to the **first node clockwise** from its position.

```
        0
     N1 .  k1
   .         .
 k3            N2
   .         .
     N3 . k2
```

- k1 → N2, k2 → N3, k3 → N1.
- Add a node N4 between N3 and N1: only the keys between N3 and N4 move.
- Remove N2: only N2's keys move, to the next node clockwise.

When ownership is balanced, a new node takes over just its fair share of the ring, and only those keys move: about 20% when going from 4 to 5 nodes, against about 80% for modulo hashing. Removing a node moves only that node's share.

```formula reference
f_mod ≈ N / (N + 1)
f_ring ≈ 1 / (N + 1)
where
f_mod: the fraction of keys that change node under hash-modulo placement when one node is added, assuming evenly spread hashes
f_ring: the fraction that change node under consistent hashing with balanced ownership
N: the number of nodes before adding one
≈: approximately equal to; exact only with evenly spread hashes and equal shares of the ring
In words: adding one node moves almost every key under modulo placement, but only the new node's fair share under consistent hashing. For 4 to 5 nodes that is about 80% versus about 20%.
```

> [!analogy] Real-world analogy: postal rounds on a ring road
> Houses sit around a ring road, and each house is served by the next post office you reach driving clockwise. Opening a new post office takes over only the houses between it and the previous office. Under the "house number modulo number of offices" scheme, opening one more office reassigns almost every house.
>
> **How it maps:** Houses are keys, offices are cache nodes, and their positions on the road are hash values on the ring. The clockwise rule is consistent hashing's ownership rule; the modulo scheme is `hash(key) % N`. A house that changes office is a key that misses on its new node.
>
> **Where it stops:** Real offices are placed deliberately; hash positions are effectively random, so one node can get a long stretch of road. Virtual nodes (below) fix that by giving each office many small stretches.

The problem with one point per node is uneven arcs: one node may own 40% of the ring. The fix is **virtual nodes**: each physical node is placed at many ring positions, perhaps 150 in an illustrative design; choose and measure the count for the implementation. Arc sizes average out, and when a node fails its load is spread across many survivors rather than dumped on one neighbour.

Memcached clients and proxies can use the **ketama** consistent hashing algorithm; check the client’s configured distribution policy. Amazon's Dynamo and Cassandra use the same idea for databases.

## Key takeaways
- Changing hash-modulo node counts remaps most keys; adjacent counts preserve only a small fraction.
- Consistent hashing moves the new node’s share when ownership is balanced.
- Many virtual positions per physical node smooth ring ownership and distribute a failed node’s keys across survivors.

## Further reading
- [Consistent hashing — Wikipedia](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Dynamo: Amazon’s Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
