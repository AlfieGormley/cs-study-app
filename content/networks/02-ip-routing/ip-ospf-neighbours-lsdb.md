---
id: ip-ospf-neighbours-lsdb
title: Build an OSPF link-state database
level: intermediate
minutes: 3
sourceLesson: ip-interior-routing
summary: Trace OSPF neighbour discovery, adjacency selection, scoped OSPF LSA flooding and route computation.
---

Trace OSPF neighbour discovery, adjacency selection, scoped OSPF LSA flooding and route computation.

## Link state and OSPF

### The idea

Instead of sharing distances, every router shares the raw facts about its own links. Everyone collects everyone's facts into the same map, then independently runs **Dijkstra's shortest-path algorithm** on it. After the relevant databases and computations converge, routers can agree on valid shortest-path forwarding. During updates, transient disagreement and forwarding microloops remain possible.

**Open Shortest Path First** includes OSPFv2 (RFC 2328) for IPv4 and OSPFv3, originally for IPv6. OSPFv3 address-family extensions also support IPv4 (RFC 5838).

### How OSPF builds its map

1. **OSPF Hellos.** On enabled non-passive broadcast OSPFv2 interfaces, routers send Hello packets to 224.0.0.5. A common Cisco Ethernet configuration uses a 10-second Hello interval; other network types and configurations differ. Routers that hear each other and agree on parameters (area, timers, subnet) become **OSPF neighbours**. If no Hello arrives for the dead interval (40 seconds in that Cisco Ethernet configuration), the neighbour is declared down.
2. **Database sync.** Neighbours selected for adjacency exchange database description (DBD) packets and request missing LSAs. On a broadcast LAN, two DROther neighbours normally remain in the Two-Way state rather than forming a full adjacency; each instead synchronises its database with the DR and BDR.
3. **OSPF LSA flooding.** Router/network **link-state advertisements** (LSAs) describe area topology and are propagated within that area. LSA types have different scopes. Sequence numbers, checksums and age distinguish instances; standard self-originated LSAs are refreshed every LSRefreshTime, 1,800 seconds (30 minutes), even without a topology change, subject to protocol extensions.
4. **SPF.** Each router computes paths from its area **link-state database** (LSDB), using Dijkstra with itself as the root of the area topology. Inter-area and external routes require additional selection steps.

A detected failure causes affected originators to update LSAs. Depending on topology, DR role and changed reachability, more than the two link endpoints can originate updates. SPF scheduling, OSPF LSA flooding and forwarding installation determine how quickly routing convergence completes. Tuned designs can recover quickly, but no sub-second bound applies universally.

OSPF runs directly over IP (protocol 89), not over TCP or UDP, and handles its own reliability with acknowledgements.

## Pitfalls

- **Mismatched Hello or dead timers, MTU or area IDs**: OSPF neighbours get stuck short of full adjacency.
- **Inconsistent reference bandwidth** across routers gives asymmetric, surprising paths.
- **Flapping links** cause repeated SPF runs; implementations throttle SPF and LSA generation to stay stable.
- **Redistribution loops** between two protocols (OSPF into RIP and back) can create routing loops that neither protocol can see.

## Key takeaways
- OSPF routers build scoped link-state maps and compute paths after convergence.
- Not every pair of broadcast neighbours forms a full adjacency.
- Hello/dead intervals, area checks and database-exchange checks affect adjacency.
- Convergence includes detection, OSPF LSA flooding, computation and forwarding installation; no universal timing bound follows.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [Open Shortest Path First — Wikipedia](https://en.wikipedia.org/wiki/Open_Shortest_Path_First)
- [Distance-vector routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)

- [RFC 5838: OSPFv3 address families](https://www.rfc-editor.org/rfc/rfc5838.html)
- [Cisco OSPF FAQ: costs and operational details](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html)
