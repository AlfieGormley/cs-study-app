---
id: hash-function-server-placement
title: Hash placement when server counts change
level: intermediate
minutes: 3
sourceLesson: hash-functions
summary: This unit applies bucket reduction to server placement.
---

This unit applies bucket reduction to server placement. The issue is not a bad collision rate: changing the divisor can remap data even when the original hash is excellent.

## Hashing in distributed systems

Hashing also decides which server stores a key in a sharded cache or database. The naive rule reduces the key’s stable full hash modulo the server count to select a server. It works until N changes, because the remainder changes for most keys:

```formula
F ≈ N / (N + 1)
F ≈ 10 / 11 ≈ 0.91
where
F: the fraction of keys that move to a different server when one server is added, from 0 to 1
N: the number of servers before the change, here 10
≈: approximately equal to (it assumes uniformly spread hashes)
In words: going from 10 to 11 servers with mod-N placement moves about 10 keys in every 11, roughly 91% of the data, even though only one server was added.
```

Doubling N moves about half the keys. Either way a large share of a cache is invalidated at once, which is why distributed systems use **consistent hashing**, which ideally moves the new server’s balanced share of keys. That is covered in the System Design subject.

## Why the remapping matters

Consider cached customer profiles placed across ten numbered servers. When an eleventh server is added, recomputing a remainder can direct a request to a different server even if the profile’s full hash and contents never changed. The old copy may still be present on its former server, but the new lookup rule will not visit it. A cache must then refill or migrate the entry; a database must coordinate movement and ownership more carefully.

Consistent hashing instead assigns positions on a ring. Adding an owner changes only the intervals it takes over. The ideal movement fraction assumes balanced ownership and uniformly distributed keys; finite rings, skewed workloads and replication can change the amount of data or traffic that moves. It is not a guarantee that every physical server receives exactly an equal share.

Do not confuse remapping with hash randomisation. A per-process string hash is unsuitable as a stable cross-process placement hash: the clients and servers must agree on the same hash and placement configuration. A stable distributed hash can still need a separate defence if untrusted clients deliberately choose hot keys. This unit concerns placement changes, while the preceding flooding unit concerns pathological collision work.

```formula
F_ring ≈ 1 / (N + 1)
F_ring ≈ 1 / 11 ≈ 0.091
where
F_ring: the fraction of keys that change owner under ideal balanced consistent hashing, dimensionless
N: the old server count, here ten
≈: approximately equal; assumes balanced ownership and uniformly distributed keys
In words: Adding an eleventh server ideally moves about nine per cent of keys, rather than about ninety-one per cent under remainder placement.
```

## Key takeaways
- Changing the server-count divisor can remap most keys.
- Ideal balanced consistent hashing moves only the new owner’s share.
- Distributed placement needs an agreed stable hash and configuration.

## Further reading
- [Consistent hashing original paper](https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf)
