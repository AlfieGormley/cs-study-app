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

The simplest way to pick a node is to turn the key into a number and take the remainder after dividing by the number of nodes:

```formula
node = hash(key) mod N
where
node: the index of the node that holds the key, a whole number from 0 to N − 1
hash: a hash function, which turns the key (a string) into a large, evenly spread whole number
key: the cache key, such as user:42
mod: modulo, the remainder after whole-number division; 17 mod 4 = 1; written % in most programming languages
N: the number of cache nodes
In words: hash the key and use the remainder after dividing by the node count as the node number.
```

In code this is `hash(key) % N`. For example, a key whose hash is 1,000,003 goes to node 1,000,003 mod 4 = 3 in a four-node cluster.

This spreads keys evenly, but it falls apart when N changes. Going from 4 to 5 nodes, a key stays put only if its hash leaves the same remainder when divided by 4 as when divided by 5. The pair of remainders repeats every 20 numbers (20 is the smallest number divisible by both 4 and 5), and they match only for hashes that leave a remainder of 0, 1, 2 or 3 when divided by 20: 4 cases in 20. In general, growing from N to N + 1 nodes:

```formula
f_stay = 1 / (N + 1)
f_move = N / (N + 1)
f_move = 4 / (4 + 1) = 0.8
where
f_stay: the fraction of keys that keep their node
f_move: the fraction of keys that move to a different node
N: the number of nodes before adding one, here 4
In words: adding one node to N under hash-mod-N moves all but one key in N + 1, so the bigger the cluster, the worse it gets.
```

So about **1 in 5** keys stay, and **80%** of keys suddenly live on a different node, all of them missing at once. For a cache, that is a self-inflicted stampede on the database.

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

When the points are evenly spread, the new node ends up with an equal share of the ring, and that share is all that moves:

```formula
f_move ≈ 1 / (N + 1)
f_move ≈ 1 / (4 + 1) = 0.2
where
f_move: the fraction of keys that move when one node is added
N: the number of nodes before adding one, here 4
≈: approximately equal to; exact only when every node owns an equal arc of the ring
In words: adding a node takes over just its fair share of keys, about one in N + 1, instead of almost all of them.
```

Going from 4 to 5 nodes moves about 20% of keys, against 80% for hash mod N. Removing a node moves only that node's share, about 1 / N of the keys.

The problem with one point per node is uneven arcs: one node may own 40% of the ring. The fix is **virtual nodes**: each physical node is placed at many ring positions, perhaps 150 in an illustrative design; choose and measure the count for the implementation. Arc sizes average out, and when a node fails its load is spread across many survivors rather than dumped on one neighbour.

Memcached clients and proxies can use the **ketama** consistent hashing algorithm; check the client’s configured distribution policy. Amazon's Dynamo and Cassandra use the same idea for databases.

## Key takeaways
- Changing hash-modulo node counts remaps most keys; adjacent counts preserve only a small fraction.
- Consistent hashing moves the new node’s share when ownership is balanced.
- Many virtual positions per physical node smooth ring ownership and distribute a failed node’s keys across survivors.

## Further reading
- [Consistent hashing — Wikipedia](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Dynamo: Amazon’s Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
