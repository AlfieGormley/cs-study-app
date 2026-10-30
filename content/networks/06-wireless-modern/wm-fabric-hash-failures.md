---
id: wm-fabric-hash-failures
title: Hash imbalance, remapping and flowlets
level: intermediate
minutes: 4
summary: Uniform independent flow selection still produces empty paths and elephant collisions.
sourceLesson: wm-datacentre
---

Flow hashing keeps each connection on one path, but it chooses paths blindly. That causes three recurring problems in real fabrics: big flows piling onto one link, healthy flows being reshuffled when a link fails, and different switch tiers making the same unlucky choices.

## Where ECMP goes wrong

**Elephant flows collide.** With many similarly sized flows, hashing spreads load roughly evenly. A few large flows (backups, replication, ML training) are different: two of them can land on the same link while others sit idle, because the hash knows nothing about load.

> [!example] How lumpy is hashing?
> Assume 8 equal flows choose independently and uniformly among 8 paths. The chance that every path gets exactly one flow is only about 0.24%, and on average about a third of the paths (about 2.7 of 8) carry no flow at all. With just two flows on four paths, they share a path one time in four. Actual unused bandwidth also depends on flow demand and other traffic.

Mitigations include **flowlet switching** (changing path after a gap intended to exceed the path-delay difference; the guarantee depends on that delay bound), congestion-aware load balancing in the fabric, and **packet spraying** with transports that tolerate reordering. Applications can also split big transfers over several connections.

**Rehashing on failure.** With simple modulo selection, the chosen uplink is the hash's remainder after dividing by the number of paths. If one of four uplinks fails, the switch starts dividing by three instead, and the remainders change for most hash values, not just those that used the failed link:

```
h     0 1 2 3 4 5 6 7 8 9 10 11
mod4  0 1 2 3 0 1 2 3 0 1 2  3
mod3  0 1 2 0 1 2 0 1 2 0 1  2
same  y y y . . . . . . . .  .
```

The pattern repeats every 12 values. Only 3 of every 12 hash values (a quarter of all flows) keep the same uplink; the flows that were on uplink 3 must move, and so must about two-thirds of the flows on the *healthy* links. In general, with uniform hashes and the last of N paths removed, only about 1 flow in N keeps its path, so the more paths there were, the larger the share of healthy flows that move.

Moved flows can see reordering, and anything holding per-flow state behind ECMP, such as a fleet of stateful load balancers, may receive flows it has never seen. **Resilient hashing** aims to minimise remapping: on a simple removal it can move only the failed path's flows and leave healthy assignments alone. How a switch assigns hash buckets and rebalances them determines whether additional flows move.

**Polarisation.** Correlated hash choices across tiers can underuse some paths, especially with matching path counts and mappings. Different hash seeds or inputs can reduce this polarisation.

## Key takeaways
- Uniform independent flow selection still produces empty paths and elephant collisions.
- Modulo path-count changes remap healthy flows too; resilient hashing targets that disruption.
- Flowlet reordering protection depends on a valid path-delay bound.

## Further reading
- [RFC 2992: Analysis of an Equal-Cost Multi-Path Algorithm](https://www.rfc-editor.org/rfc/rfc2992)
- [Google: Maglev load-balancer design](https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/)
