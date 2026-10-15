---
id: ip-ospf-worked-spf
title: Trace shortest-path first in Python
level: intermediate
minutes: 4
sourceLesson: ip-interior-routing
summary: Run the worked Dijkstra trace and carry each shortest path’s first hop into a forwarding decision.
---

Run the worked Dijkstra trace and carry each shortest path’s first hop into a forwarding decision.

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

The same calculation in Python:

```python
import heapq
import itertools

def spf(graph, src):
    if src not in graph:
        raise ValueError("unknown source")
    for edges in graph.values():
        for v, c in edges:
            if (v not in graph
                    or type(c) is not int
                    or c < 0):
                raise ValueError("bad edge")
    dist, hop = {src: 0}, {src: None}
    order = itertools.count()
    pq = [(0, next(order), src)]
    done = set()
    while pq:
        # Skip repeated settled nodes.
        d, _, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v, c in graph[u]:
            nd = d + c
            old = dist.get(v, float("inf"))
            # Save the improved path.
            if nd < old:
                dist[v] = nd
                if u == src:
                    hop[v] = v
                else:
                    hop[v] = hop[u]
                heapq.heappush(
                    pq,
                    (nd, next(order), v))
    return dist, hop
```

This simple-graph model uses reusable adjacency lists and accepts nonnegative integer costs, chooses one first hop, and does not implement full OSPF or ECMP. The counter avoids comparing node objects on equal heap priorities. With lazy heap entries and a simple graph, the usual bound is:

```formula
T = O((V + E) log(V))
where
T: the running time of the shortest-path calculation, counted in basic steps
O( ): Big-O notation: grows no faster than the expression inside, ignoring constant factors
V: the number of vertices (routers and networks) in the graph
E: the number of edges (links) in the graph
log: the logarithm, here of V; it grows very slowly (log base 2 of 1,000 is about 10), and its base only changes a constant factor, which Big-O ignores
In words: the work grows roughly with the size of the map, times a slowly growing factor for keeping the queue of candidates in order.
```

So a map with 1,000 routers and 3,000 links needs on the order of (1,000 + 3,000) × 10 = 40,000 basic steps, treating bounded integer arithmetic as constant cost. Runtime still depends on graph size and implementation; no measured performance is claimed.

## Key takeaways
- Settle the least-distance candidate and relax outgoing links.
- The teaching model accepts nonnegative integer costs and returns one first hop.
- A counter prevents equal heap priorities from comparing node objects.
- The example is a graph calculation, not a complete OSPF implementation or performance benchmark.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [Open Shortest Path First — Wikipedia](https://en.wikipedia.org/wiki/Open_Shortest_Path_First)
- [Distance-vector routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)

- [RFC 5838: OSPFv3 address families](https://www.rfc-editor.org/rfc/rfc5838.html)
- [Cisco OSPF FAQ: costs and operational details](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html)
