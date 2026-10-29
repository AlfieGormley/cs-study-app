---
id: ip-ospf-worked-spf
title: Trace a shortest-path-first calculation
level: intermediate
minutes: 3
sourceLesson: ip-interior-routing
summary: Follow a Dijkstra trace and carry each shortest path’s first hop into a forwarding decision.
---

Every OSPF router runs the same calculation on its copy of the area map: Dijkstra's shortest-path-first algorithm, with itself as the starting point. Tracing one small example shows why a directly connected neighbour is not always reached over the direct link.

### A worked SPF

```
 A --1-- B
 |       |
 5       2
 |       |
 C --1-- D
 |       |
 3       5
 |       |
 +-- E --+
```

Dijkstra from A. Repeatedly settle the closest unsettled node and relax its links:

| Settle | Dist | Updates |
|---|---|---|
| A | 0 | B at 1, C at 5 |
| B | 1 | D at 3 |
| D | 3 | C at 4 (was 5), E at 8 |
| C | 4 | E at 7 (was 8) |
| E | 7 | none |

Every shortest path from A to another vertex in this graph starts via B, even to C, which A is directly connected to. A–B–D–C costs 4, beating the direct link's 5. A forwarding entry needs next-hop/interface information rather than the full path; implementations also retain metrics and other routing metadata.

Two properties make this work. Dijkstra settles nodes in order of distance, so once a node is settled its distance is final; that relies on link costs never being negative, which OSPF guarantees. And the router only needs the **first hop** of each shortest path for forwarding: every router on the path runs the same calculation on the same map, so each makes a consistent next choice.

The work grows roughly with the size of the map. With a binary-heap priority queue, the usual bound is O((V + E) log V), where V is the number of routers and networks and E the number of links. Implementations also limit how often SPF runs (throttling) and can recalculate incrementally; no measured run time is claimed here.

## Key takeaways
- Settle the least-distance candidate and relax outgoing links.
- Settled distances are final because costs are never negative.
- Forwarding needs only each shortest path's first hop; consistent maps give consistent choices.
- The example is a graph calculation, not a complete OSPF implementation or performance benchmark.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
