---
id: ip-interior-routing
title: RIP vs OSPF
level: intermediate
minutes: 16
summary: How routers inside one network learn their tables automatically, comparing distance-vector RIP and its count-to-infinity problem with link-state OSPF, Dijkstra, costs, areas and designated routers.
---

The last lesson assumed the routing table was already full. In a network of three routers you could type the routes in by hand. In a network of three hundred, with links failing and being added, you need routers to work it out themselves.

That's what **routing protocols** do. **Interior gateway protocols** (IGPs) operate within a routing domain. An **autonomous system** is an administratively coordinated network or group of networks with a routing policy; one organisation can operate multiple ASes. BGP exchanges inter-AS routes and is also used internally.

There are two classic designs:

- **Distance vector**: each router tells its neighbours "here's how far I am from everything". Nobody sees the whole map. RIP is the textbook example.
- **Link state**: routers flood link information within the relevant scope, such as an OSPF area. Each router builds that scope's map and computes shortest paths itself. OSPF and IS-IS work this way.

## Distance vector and RIP

### The idea

Each router keeps a table of `destination -> (distance, next hop)`. Periodically it sends that table to its neighbours. When it hears a neighbour's table, it applies the **Bellman–Ford** rule:

```formula
D(x, d) = min_n (c(x, n) + D(n, d))
where
D(x, d): router x's best known distance (total cost) to destination d; for a neighbour n, D(n, d) is the distance n advertised
x: the router doing the calculation
d: the destination network
n: one of x's neighbours; the rule tries every neighbour in turn
c(x, n): the cost of the link from x to neighbour n (1 per hop in RIP)
min_n: the minimum over all neighbours n: the smallest of the values computed for each neighbour
In words: my best distance to a destination is the cheapest "hop to a neighbour, then their distance", and the neighbour that gives it becomes my next hop.
```

For example, router X hears from neighbour Y (link cost 2), which advertises network N at distance 7, and from neighbour Z (link cost 5), which advertises N at 3:

```formula
D(X, N) = min(2 + 7, 5 + 3)
D(X, N) = min(9, 8) = 8
where
D(X, N): router X's best distance to network N
X: the router doing the calculation
N: the destination network
min: the smallest of the values in the brackets
In words: going via Y costs 9 and via Z costs 8, so X installs N at distance 8 with Z as its next hop, even though the link to Y is cheaper.
```

Routers only ever know what their neighbours told them. It's routing by rumour.

### RIP specifics

The **Routing Information Protocol** provides a compact distance-vector example:

| Property | RIP |
|---|---|
| Metric | Additive integer cost, normally hop count |
| Infinity | 16 (max usable 15) |
| Updates | Periodic eligible-route updates around 30 s, plus triggered updates |
| Transport | UDP port 520 |
| Route timeout | 180 s without refresh |

**RIPv1** (1988) was classful: it didn't send subnet masks and broadcast its updates. **RIPv2** (RFC 2453) carries masks (so CIDR works), uses multicast 224.0.0.9 and supports authentication. **RIPng** is the IPv6 version.

With cost 1 per link, RIP reduces to hop count: two 10 Gbit/s links cost more than one 1 Mbit/s link. RFC 2453 also permits configured higher network costs; RIP does not automatically measure bandwidth. The maximum usable advertised route metric is 15, which is deliberate, for reasons the next section explains.

### Count to infinity

Distance vector has a famous failure. Take three routers in a line, with network N attached to C:

```
 N --- C ------ B ------ A
      d=1      d=2      d=3
```

B reaches N via C at 2 hops, A via B at 3. Now the **B–C link fails**.

Assume plain distance vector without split horizon, poison reverse or an effective hold-down, and that A has not yet learned the failure. B has lost its route. But A's next periodic update says "I can reach N in 3". B doesn't know that A's path *goes through B*, so it believes it:

| Step | B's distance | A's distance |
|---|---|---|
| Before | 2 via C | 3 via B |
| B hears A | 4 via A | 3 via B |
| A hears B | 4 via A | 5 via B |
| B hears A | 6 via A | 5 via B |
| ... | ... | ... |
| End | 16 | 16 |

The two routers bounce the route between them, adding one each time, until it hits 16 and is declared unreachable. Meanwhile packets for N loop between A and B until their TTL runs out. With 30-second updates this can take minutes. That's why RIP's infinity is so small: a larger one would make the count take longer still.

### The fixes

- **Split horizon**: never advertise a route back out of the interface you learnt it from. A learnt N from B, so A doesn't tell B about N. That alone fixes the example above.
- **Poison reverse**: stronger version: *do* advertise it back, but with metric 16 ("don't route via me").
- **Triggered updates**: send changes without waiting for the next periodic update, with a small randomised rate-limiting delay to prevent storms.
- **Hold-down**: some implementations temporarily restrict acceptance of alternatives after failure. Exact rules vary; this is not a universal RIP requirement and can delay valid recovery.

None of these is complete. Simple split horizon prevents the immediate reverse advertisement in this example, but an existing two-router loop may need to time out; poison reverse explicitly advertises infinity to break it. Neither mechanism prevents every loop through three or more routers. Other distance-vector protocols use additional loop-avoidance algorithms; this limitation of basic RIP is not a proof that all distance-vector designs behave identically.

## Link state and OSPF

### The idea

Instead of sharing distances, every router shares the raw facts about its own links. Everyone collects everyone's facts into the same map, then independently runs **Dijkstra's shortest-path algorithm** on it. After the relevant databases and computations converge, routers can agree on valid shortest-path forwarding. During updates, transient disagreement and forwarding microloops remain possible.

**Open Shortest Path First** includes OSPFv2 (RFC 2328) for IPv4 and OSPFv3, originally for IPv6. OSPFv3 address-family extensions also support IPv4 (RFC 5838).

### How OSPF builds its map

1. **OSPF Hellos.** On enabled non-passive broadcast OSPFv2 interfaces, routers send Hello packets to 224.0.0.5. A common Cisco Ethernet configuration uses a 10-second Hello interval; other network types and configurations differ. Routers that hear each other and agree on parameters (area, timers, subnet) become **OSPF neighbours**. If no Hello arrives for the dead interval (40 seconds in that Cisco Ethernet configuration), the neighbour is declared down.
2. **Database sync.** Neighbours selected for adjacency exchange database description (DBD) packets and request missing LSAs. On a broadcast LAN, two DROther neighbours normally remain in the Two-Way state rather than forming a full adjacency; each instead synchronises its database with the DR and BDR.
3. **Flooding.** Router/network **link-state advertisements** (LSAs) describe area topology and are flooded within that area. LSA types have different scopes. Sequence numbers, checksums and age distinguish instances; standard self-originated LSAs are refreshed every LSRefreshTime, 1,800 seconds (30 minutes), even without a topology change, subject to protocol extensions.
4. **SPF.** Each router computes paths from its area **link-state database** (LSDB), using Dijkstra with itself as the root of the area topology. Inter-area and external routes require additional selection steps.

A detected failure causes affected originators to update LSAs. Depending on topology, DR role and changed reachability, more than the two link endpoints can originate updates. SPF scheduling, flooding and forwarding installation determine how quickly routing convergence completes. Tuned designs can recover quickly, but no sub-second bound applies universally.

OSPF runs directly over IP (protocol 89), not over TCP or UDP, and handles its own reliability with acknowledgements.

### Cost

Each interface has an **OSPF cost**, and a path's cost is the sum along it. Some implementations derive the interface cost from configured bandwidth:

```formula
C = max(1, ⌊R / B⌋)
C = max(1, ⌊100 / 10⌋) = 10
C = max(1, ⌊100 / 1000⌋) = max(1, 0) = 1
where
C: the OSPF cost of the interface: a whole number with no unit; lower means more attractive
R: the reference bandwidth, in megabits per second (Mbit/s); 100 Mbit/s by default in classic Cisco IOS
B: the interface's configured bandwidth, in Mbit/s (1 Gbit/s = 1,000 Mbit/s)
⌊ ⌋: floor: round down to a whole number, since costs are integers
max(1, …): the larger of 1 and the value after it, so the cost never falls below 1
Mbit/s: megabits per second: millions of bits per second
In words: divide the reference by the link's bandwidth, drop any fraction, and use 1 if that gives 0. A 10 Mbit/s link costs 10, but a 1 Gbit/s link also only costs 1, the same as 100 Mbit/s.
```

Classic Cisco IOS documentation uses a **100 Mbit/s** default reference, with a minimum positive interface cost of 1. Other platforms have different defaults, and cost can be manually configured; OSPF itself does not mandate this bandwidth formula. So:

| Link | Cost (ref 100M) | Cost (ref 100G) |
|---|---|---|
| 10 Mbit/s | 10 | 10,000 |
| 100 Mbit/s | 1 | 1,000 |
| 1 Gbit/s | 1 | 100 |
| 10 Gbit/s | 1 | 10 |

> [!warning] The 100 Mbit/s trap
> With the default, a 100 Mbit/s link and a 10 Gbit/s link both cost 1, so those interfaces have equal cost; hop structure and other costs then determine the path. Set the reference bandwidth higher (say 100 Gbit/s) on **every** router, consistently, or costs won't mean what you think.

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
| A | 0 | B=1, C=5 |
| B | 1 | D=3 |
| D | 3 | C=4 (was 5), E=8 |
| C | 4 | E=7 (was 8) |
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
        d, _, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for v, c in graph[u]:
            nd = d + c
            old = dist.get(v, float("inf"))
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
T = O((V + E) × log V)
where
T: the running time of the shortest-path calculation, counted in basic steps
O( ): Big-O notation: grows no faster than the expression inside, ignoring constant factors
V: the number of vertices (routers and networks) in the graph
E: the number of edges (links) in the graph
log: the logarithm, here of V; it grows very slowly (log base 2 of 1,000 is about 10), and its base only changes a constant factor, which Big-O ignores
In words: the work grows roughly with the size of the map, times a slowly growing factor for keeping the queue of candidates in order.
```

So a map with 1,000 routers and 3,000 links needs on the order of (1,000 + 3,000) × 10 = 40,000 basic steps, treating bounded integer arithmetic as constant cost. Runtime still depends on graph size and implementation; no measured performance is claimed.

### Areas

Flooding every LSA to every router and rerunning SPF on every change doesn't scale forever. OSPF splits a network into separate **OSPF areas**:

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

On a shared segment like an Ethernet LAN, full adjacency between every pair of routers would grow quickly with their number. Instead the routers elect a **designated router** (DR) and a backup (BDR). Everyone forms full adjacencies only with those two, and the DR describes the shared segment in a single LSA.

```formula
A_mesh = n × (n − 1) / 2
A_DR = 2 × (n − 2) + 1
A_mesh = 10 × 9 / 2 = 45
A_DR = 2 × 8 + 1 = 17
where
A_mesh: the number of full adjacencies if every pair of routers formed one
A_DR: the number of full adjacencies with a DR and BDR
n: the number of OSPF routers on the shared segment, here 10
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
| Convergence | Depends on updates, failures and timers | Depends on detection, flooding, computation and installation |
| Scale | Maximum usable metric 15 | Area design and implementation constrain scale |
| Config | Interfaces, routes, timers and policy | Areas, costs, timers and policy |

Other protocols include link-state **IS-IS** and distance-vector **EIGRP** with DUAL loop-avoidance logic. BGP can also be used within a data-centre fabric; RFC 7938 describes one such design rather than a universal deployment rule.

> [!note] Content omitted after review
> Protocol market-share rankings, universal router-count limits and measured convergence-time comparisons are absent because no applicable deployment survey or benchmark was established. The worked SPF graph is a mathematical example, not a router benchmark.

## Pitfalls

- **Mismatched Hello or dead timers, MTU or area IDs**: OSPF neighbours get stuck short of full adjacency.
- **Inconsistent reference bandwidth** across routers gives asymmetric, surprising paths.
- **Flapping links** cause repeated SPF runs; implementations throttle SPF and LSA generation to stay stable.
- **Redistribution loops** between two protocols (OSPF into RIP and back) can create routing loops that neither protocol can see.

## Key takeaways
- Distance-vector routers share distances with neighbours and apply Bellman–Ford; link-state routers flood link facts and each run Dijkstra on the full map.
- RIP normally uses unit-cost hops, with 16 as infinity and is prone to count to infinity; split horizon, poison reverse, triggered updates and hold-down reduce but don't eliminate it.
- OSPF discovers neighbours with Hellos, synchronises scoped LSDBs and computes routes; transient inconsistency can still occur during routing convergence.
- OSPF costs are configurable. With the described 100 Mbit/s reference formula, interfaces at or above that bandwidth all reach the minimum cost.
- Areas limit flooding and SPF scope; designated routers cut adjacencies on shared segments.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [Open Shortest Path First — Wikipedia](https://en.wikipedia.org/wiki/Open_Shortest_Path_First)
- [Distance-vector routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)

- [RFC 5838: OSPFv3 address families](https://www.rfc-editor.org/rfc/rfc5838.html)
- [Cisco OSPF FAQ: costs and operational details](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html)
