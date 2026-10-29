---
id: ip-igp-distance-vector
title: Learn routes with distance vectors
level: intermediate
minutes: 4
sourceLesson: ip-interior-routing
summary: Explain the Bellman–Ford neighbour rule and interpret the RIP metric and update rules.
---

The forwarding lessons assumed the routing table was already full. In a network of three routers you could type the routes in by hand. In a network of three hundred, with links failing and being added, you need routers to work it out themselves.

That's what **routing protocols** do. **Interior gateway protocols** (IGPs) operate within a routing domain. An **autonomous system** is an administratively coordinated network or group of networks with a routing policy; one organisation can operate multiple ASes. BGP exchanges inter-AS routes and is also used internally.

There are two classic designs:

- **Distance vector**: each router tells its neighbours "here's how far I am from everything". Nobody sees the whole map. RIP is the textbook example.
- **Link state**: routers propagate link information within the relevant scope, such as an OSPF area. Each router builds that scope's map and computes shortest paths itself. OSPF and IS-IS work this way.

## Distance vector and RIP

### The idea

Each router keeps a table of `destination -> (distance, next hop)`. Periodically it sends that table to its neighbours. When it hears a neighbour's table, it applies the **Bellman–Ford** rule:

```formula essential
D(x, d) = min_n (c(x, n) + D(n, d))
where
D(x, d): router x's best known distance (total routing cost) to destination d; for a neighbour n, D(n, d) is the distance n advertised
x: the router doing the calculation
d: the destination network
n: one of x's neighbours; the rule tries every neighbour in turn
c(x, n): the cost of the link from x to neighbour n (normally 1 per network in RIP; larger configured costs are permitted)
min_n: the minimum over all neighbours n: the smallest of the values computed for each neighbour
In words: my best distance to a destination is the cheapest "hop to a neighbour, then their distance", and the neighbour that gives it becomes my next hop.
```

For example, router X hears from neighbour Y (routing link cost 2), which advertises network N at distance 7, and from neighbour Z (routing link cost 5), which advertises N at 3. Via Y the total is 2 + 7 = 9; via Z it is 5 + 3 = 8. X installs N at distance 8 with Z as next hop, even though the link to Y is cheaper: what matters is the whole journey, not the first step.

Routers only ever know what their neighbours told them. It's routing by rumour.

> [!analogy] Real-world analogy: Village signposts
> Imagine each village crossroads has signposts that are repainted from what neighbouring villages say: "the castle is 7 miles via Ashby" or "3 miles via Bramley". The local painter adds the distance to that neighbour and keeps whichever sign gives the shortest total. Nobody holds a full map.
>
> **How it maps:** Each crossroads is a router, the signposts are its routing table (distance and next hop per destination), and the neighbours' reports are distance-vector updates. The painter's rule is the Bellman–Ford update.
>
> **Where it stops:** Real signposts are rarely wrong for long, but a router keeps believing a neighbour's claim until updates or timers correct it. If a bridge collapses, two villages can each point at the other, which is the count-to-infinity problem in the next lesson.

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

## Key takeaways
- An IGP operates within a routing domain; distance vector and link state exchange different information.
- Add the local routing link cost to each neighbour’s advertised distance and choose the minimum.
- RIP uses additive costs, normally hop count, with 16 meaning unreachable.
- RIPv2 carries masks and uses UDP port 520; configured costs need not measure bandwidth.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [Open Shortest Path First — Wikipedia](https://en.wikipedia.org/wiki/Open_Shortest_Path_First)
- [Distance-vector routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)

- [RFC 5838: OSPFv3 address families](https://www.rfc-editor.org/rfc/rfc5838.html)
- [Cisco OSPF FAQ: costs and operational details](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html)
