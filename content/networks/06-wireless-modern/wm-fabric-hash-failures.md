---
id: wm-fabric-hash-failures
title: Hash imbalance, remapping and flowlets
level: intermediate
minutes: 4
summary: Uniform independent flow selection still produces empty paths and elephant collisions.
sourceLesson: wm-datacentre
---

This unit focuses on hash imbalance, remapping and flowlets. It builds on the earlier units in this module; the examples below state their additional assumptions.

## Where ECMP goes wrong

**Elephant flows collide.** With well-distributed keys and enough similarly sized flows, hashing can spread load approximately evenly. A few large flows (backups, replication, ML training) can land on the same link while others sit idle.

> [!example] How lumpy is hashing?
> Assume 8 equal flows choose independently and uniformly among 8 paths. The chance that every path gets exactly one is only about 0.24%, and on average about a third of the paths carry no flow at all. Actual unused bandwidth also depends on flow demand and other traffic.

The calculation behind that example:

```formula
P_even = n! / n^n
P_even = 40,320 / 16,777,216 ≈ 0.0024
E_empty = n(1 − (1/n))^n
E_empty = 8 × (7/8)^8 ≈ 2.7
where
P_even: the probability that every path gets exactly one flow
n: the number of flows and also the number of paths, 8 here
n!: n factorial, 1 × 2 × … × n; 8! = 40,320 is the number of ways to put 8 flows on 8 paths one each
n^n: n to the power n; 8^8 = 16,777,216 is the number of ways the 8 flows can choose among 8 paths
E_empty: the expected (average) number of paths that get no flow
(1 − 1/n)^n: the chance that one particular path is missed by all n flows; (7/8)^8 ≈ 0.34
≈: approximately equal to
In words: perfect balance almost never happens by chance, and on average about 2.7 of 8 paths (a third) sit idle.
```

Mitigations include **flowlet switching** (changing path after a gap intended to exceed the path-delay difference; the guarantee depends on that delay bound), congestion-aware load balancing in the fabric, and **packet spraying** with transports that tolerate reordering. Applications can also split big transfers over several connections.

**Rehashing on failure.** Consider uniformly distributed hash values and next-hop labels zero through three. If the last-labelled path fails, the survivors retain labels zero through two and the switch changes from taking the hash remainder after division by four to taking its remainder after division by three. A flow keeps its physical path only if both remainders agree. The card generalises this last-member-removal model:

```formula
f_keep = 1 / N
f_keep = 1 / 4 = 25%
where
f_keep: the fraction of all flows whose next hop stays the same when the path count drops from N to N − 1
N: the number of paths before the failure, 4 here
In words: out of every N × (N − 1) consecutive hash values, only the first N − 1 give the same remainder both ways, so just 1 in N flows stays put.
```

For uniform hashes and a stable ordering of the three surviving next hops, about a quarter of all flows keep their old physical path: most flows on *healthy* links move too, potentially causing reordering or disrupting unsynchronised per-flow state, such as a fleet of stateful load balancers behind ECMP. **Resilient hashing** aims to minimise remapping and can preserve healthy assignments on a simple removal. Bucket policies, rebalancing and implementation details determine whether additional flows move.

**Polarisation.** Correlated hash choices across tiers can underuse some paths, especially with matching path counts and mappings. Different hash seeds or inputs can reduce this polarisation.

## Key takeaways
- Uniform independent flow selection still produces empty paths and elephant collisions.
- Modulo path-count changes remap healthy flows too; resilient hashing targets that disruption.
- Flowlet reordering protection depends on a valid path-delay bound.

## Further reading
- [RFC 2992: Analysis of an Equal-Cost Multi-Path Algorithm](https://www.rfc-editor.org/rfc/rfc2992)
- [Google: Maglev load-balancer design](https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/)
