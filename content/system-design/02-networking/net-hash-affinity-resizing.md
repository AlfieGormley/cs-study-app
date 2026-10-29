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

Naive hashing sends each key to server number `hash(key) % N`: the remainder when the key's hash is divided by the number of servers `N`. That works until `N` changes. A key keeps its server only if dividing its hash by the old and the new server count leaves the same remainder, which happens for only about one key in `N + 1`.

So going from 10 to 11 servers remaps about **91%** (10 in 11) of keys. Every cache is effectively flushed at once, and the misses land on the database behind it: a stampede of misses caused by adding capacity.

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

Adding or removing a server only moves the keys in its arc. On average a joining server takes over one share of the enlarged ring, so adding an 11th server to 10 moves about 9% (1 in 11) of keys instead of 91%. A leaving server hands over its former share.

> [!analogy] Real-world analogy: Counting off into groups versus a round table
> A teacher splits a class into 10 groups by having pupils count off "1 to 10" along a line. Add an 11th group and recount, and almost everyone gets a new group. Now seat the pupils around a round table with the group helpers spaced among them, and each pupil joins the next helper clockwise. A new helper who sits down takes over only the pupils just before their seat.
>
> **How it maps:** counting off is `hash(key) % N`, so changing N changes nearly every key's server. The round table is the consistent-hash ring, the helpers are servers and the pupils are keys, so a join moves only one arc of keys.
>
> **Where it stops:** positions on the ring come from a hash, not from where anyone chooses to sit, and with virtual nodes each server occupies many scattered places at once so its share evens out. A key that moves also lands on a cold cache, a cost the seating picture leaves out.

Each server gets many **virtual nodes** on the ring (say 100–200) so the load evens out. Variants include **rendezvous (HRW) hashing** and Google's **Maglev hashing**, which fills a fixed-size table mapping hash values to backends for fast, near-even assignment with minimal disruption. Consistent hashing is covered in more depth in the partitioning lessons; here, its job is cache affinity.

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
