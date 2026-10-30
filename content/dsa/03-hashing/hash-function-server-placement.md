---
id: hash-function-server-placement
title: Hash placement when server counts change
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: Placing keys on servers by remainder moves most keys when a server is added; consistent hashing moves only the new server's share.
---

Bucket reduction has a second life outside a single table: choosing which server stores a key. Here the problem is not a bad collision rate. Changing the divisor can move almost every key even when the hash itself is excellent.

## Hashing in distributed systems

A sharded cache or database must decide which server owns each key. The naive rule takes the key's stable full hash, divides by the number of servers N, and uses the remainder as the server number. It works until N changes, because then the remainder changes for most keys:

```formula reference
F ≈ N / (N + 1)
where
F: the fraction of keys that move to a different server when one server is added, from 0 to 1
N: the number of servers before the change
≈: approximately equal to; assumes uniformly spread hashes
In words: adding one server to N moves nearly every key, about N out of every N + 1.
```

Going from 10 to 11 servers moves about 10 keys in every 11, roughly 91% of the data, even though only one server was added. Doubling the server count moves about half. Either way a large share of a cache is invalidated at once, which is why distributed systems use **consistent hashing**: ideally only the new server's share moves, about 1 key in 11 (9%) for the same change. Consistent hashing is covered in the System Design subject.

## Why the remapping matters

Consider cached customer profiles spread across ten servers. When an eleventh server is added, recomputing the remainder sends most requests to a different server, even though each profile's hash and contents never changed. The old copy may still sit on its former server, but the new rule will not look there. A cache must refill or migrate those entries; a database must coordinate movement and ownership more carefully.

Consistent hashing instead places servers and keys on a ring, and each key belongs to the next server round the ring. Adding a server changes only the stretch of the ring it takes over. The ideal movement of only the new server's share assumes balanced ownership and uniformly distributed keys; finite rings, skewed workloads and replication change how much data or traffic actually moves.

> [!analogy] Real-world analogy: assigning parcels to delivery vans
> A depot assigns each street to a van by taking the street's number and dividing by the number of vans, using the remainder. When a new van joins, almost every street gets a different van, and every driver's local knowledge is wasted at once.
>
> **How it maps:** streets are keys, vans are servers and the remainder rule is mod-N placement. Consistent hashing is like giving each van a stretch of the ring road: a new van takes over part of one neighbour's stretch, and every other route is unchanged.
>
> **Where it stops:** a depot can reassign routes over a week; a cache sees the change instantly, as misses for every moved key. Real consistent-hashing rings also need many virtual positions per server to keep the stretches balanced.

Do not confuse remapping with hash randomisation. A per-process string hash such as Python's built-in `hash()` is unsuitable for placement: every client and server must compute the same stable hash with the same placement configuration. A stable placement hash can still need a separate defence if untrusted clients deliberately send traffic to hot keys.

## Key takeaways
- Changing the server-count divisor can remap most keys.
- Ideal balanced consistent hashing moves only the new owner’s share.
- Distributed placement needs an agreed stable hash and configuration.

## Further reading
- [Consistent hashing original paper](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf)
