---
id: net-hash-affinity-resizing
title: "Hash affinity without a resize stampede"
level: intermediate
minutes: 3
summary: "Compare modulo hashing with a consistent-hash ring and virtual nodes."
sourceLesson: net-load-balancers
---
Cache affinity needs stable key ownership while the fleet changes. This is a different objective from sending every new request to whichever server is least busy.

### Hashing and consistent hashing

Sometimes you *want* the same key to go to the same server: for example, routing by user ID to a server that has that user's data cached.

Naive hashing sends each key to server number `hash(key) % N`: the remainder when the key's hash is divided by the number of servers. It breaks when the number of servers changes:

```formula
s = h mod N
f_moved = N / (N + 1)
f_moved = 10 / 11 ≈ 0.91 = 91%
where
s: the server a key is sent to, numbered from 0 up to one less than the number of servers
h: the key's hash: a large, evenly spread whole number computed from the key (for example from a user ID)
mod: modulo: the remainder after division, so 23 mod 10 = 3
N: the number of servers before the change; here 10
f_moved: the fraction of keys that end up on a different server when the pool grows from N to N + 1 servers
≈: approximately equal to
%: per cent
In words: a key keeps its server only if dividing its hash by N and by N + 1 leaves the same remainder, which happens for just 1 key in N + 1, so almost every key moves.
```

Going from 10 to 11 servers therefore remaps about **91%** of keys, destroying every cache at once.

**Consistent hashing** places servers and keys on a ring; each key goes to the next server clockwise:

```
        S1
     /      \
  k3          k1
  |            |
  S3          S2
     \      /
        k2
k1 -> S2, k2 -> S3, k3 -> S1
```

Adding or removing a server only moves the keys in its arc, roughly one server’s share: on average one share of the old ring when a server leaves, and one share of the enlarged ring when a server joins. Adding an 11th server to 10:

```formula
f_moved ≈ 1 / (N + 1)
f_moved ≈ 1 / 11 ≈ 0.09 = 9%
where
f_moved: the fraction of keys that change server when one server joins a consistent-hashing ring
N: the number of servers before the change; here 10
≈: approximately (on average, given enough virtual nodes)
%: per cent
In words: only the keys in the new server's share of the ring move, about one in eleven here, instead of ten in eleven with modulo hashing.
```

Each server gets many **virtual nodes** on the ring (say 100–200) so the load evens out. Variants include **rendezvous (HRW) hashing** and Google's **Maglev hashing**, which builds a lookup table for fast, near-even assignment with minimal disruption. Consistent hashing is covered in more depth in the partitioning lessons; here, its job is cache affinity.

### Choosing

| Workload | Good choice |
|---|---|
| Uniform, short requests | Round robin |
| Variable request cost | Least requests / P2C |
| Many LB instances | Power of two choices |
| Cache or session affinity | Consistent hashing |
| Mixed server sizes | Weighted variants |

With only one ring point per server, random gaps can be very unequal and one failed server’s whole arc goes to its clockwise neighbour. Virtual nodes give each physical server many scattered arcs, so total ownership averages out and a failure can spread keys among several neighbours.

## Key takeaways

- Changing the modulo server count remaps most keys, creating cold-cache load.
- A consistent-hash join moves mainly the new server’s share; a removal redistributes its former share.
- Many virtual nodes smooth ownership and scatter the destinations that inherit a failed server’s keys.

## Further reading

- [Maglev (Google Research)](https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/)
- [Consistent hashing (Wikipedia)](https://en.wikipedia.org/wiki/Consistent_hashing)
