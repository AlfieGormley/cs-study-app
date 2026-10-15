---
id: ip-ospf-areas-designated
title: Scale OSPF with areas and a DR
level: intermediate
minutes: 4
sourceLesson: ip-interior-routing
summary: Separate area topology scope from inter-area information and count broadcast-LAN adjacencies.
---

Separate area topology scope from inter-area information and count broadcast-LAN adjacencies.

### Areas

Propagating every LSA to every router and rerunning SPF on every change does not scale forever. OSPF splits a network into separate **OSPF areas**:

- **Area 0** is the backbone area. Inter-area routing uses backbone connectivity, which may include configured virtual links through suitable transit areas.
- **Area border routers** (ABRs) sit between areas. Inside an area, routers see the full topology. Other areas are represented by inter-area prefix/cost information rather than their internal topology. A summary LSA need not aggregate several prefixes unless aggregation is configured.
- An internal topology change in area 3 changes that area's topology LSAs. Other areas can receive changed inter-area reachability/cost information; how much route computation is rerun depends on the implementation and affected LSA types.

```
 [area 1]--ABR--[ area 0 ]--ABR--[area 2]
                    |
                  ASBR -- external routes
```

An **ASBR** (autonomous system boundary router) injects routes from outside OSPF, for example a default route from the Internet edge.

### Designated routers

On a shared segment like an Ethernet LAN, full adjacency between every pair of routers would grow quickly with their number. Instead the routers elect a **designated router** (DR) and a backup (BDR). Assume broadcast OSPF network type, compatible settings, an elected DR and BDR, and completed database synchronisation. Each other router forms full adjacencies with those two rather than with every other router; the DR and BDR are also adjacent to each other. The DR describes the shared segment in a network LSA.

```formula
A_mesh = n(n − 1) / 2
A_DR = 2 × (n − 2) + 1
A_mesh = 10 × 9 / 2 = 45
A_DR = 2 × 8 + 1 = 17
where
A_mesh: the number of full adjacencies if every pair of routers formed one
A_DR: the number of full adjacencies with a DR and BDR
n: the number of OSPF routers on the shared segment, at least 2; here 10, under the broadcast/DR/BDR assumptions above
In words: in a full mesh each of n routers pairs with the n − 1 others, and dividing by 2 stops each pair being counted twice. With a DR and BDR, each of the other n − 2 routers forms just two adjacencies, plus one between the DR and BDR.
```

With 10 routers, that's 17 adjacencies instead of 45; with 20 it's 37 instead of 190. The mesh grows roughly with the square of n, the DR design only in proportion to n.

The election uses interface priority, then highest router ID, and is **not pre-emptive**: a newly arriving router with a higher priority does not displace an existing DR. Priority 0 makes an interface ineligible; when a DR fails an existing BDR can take over, rather than simply electing the newest highest-priority arrival.

## RIP vs OSPF

| | RIP | OSPF |
|---|---|---|
| Type | Distance vector | Link state |
| Metric | Hop-based cost | Configured interface cost |
| Knows | Neighbours' tables | Whole area map |
| Convergence | Depends on updates, failures and timers | Depends on detection, OSPF LSA flooding, computation and installation |
| Scale | Maximum usable metric 15 | Area design and implementation constrain scale |
| Config | Interfaces, routes, timers and policy | Areas, costs, timers and policy |

Other protocols include link-state **IS-IS** and distance-vector **EIGRP** with DUAL loop-avoidance logic. BGP can also be used within a data-centre fabric; RFC 7938 describes one such design rather than a universal deployment rule.

> [!note] Content omitted after review
> Protocol market-share rankings, universal router-count limits and measured convergence-time comparisons are absent because no applicable deployment survey or benchmark was established. The worked SPF graph is a mathematical example, not a router benchmark.

## Key takeaways
- Area topology LSAs stay in their OSPF LSA flooding scope; inter-area information can still change.
- ABRs connect areas and ASBRs inject external routes.
- A DR/BDR reduces full adjacencies on a compatible broadcast LAN.
- DR election is non-pre-emptive; protocol choice and convergence depend on the design.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [Open Shortest Path First — Wikipedia](https://en.wikipedia.org/wiki/Open_Shortest_Path_First)
- [Distance-vector routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)

- [RFC 5838: OSPFv3 address families](https://www.rfc-editor.org/rfc/rfc5838.html)
- [Cisco OSPF FAQ: costs and operational details](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html)
