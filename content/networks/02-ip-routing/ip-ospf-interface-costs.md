---
id: ip-ospf-interface-costs
title: OSPF interface costs and reference bandwidth
level: intermediate
minutes: 3
sourceLesson: ip-interior-routing
summary: Predict OSPF path choices under a reference-bandwidth cost model and spot when the default makes fast links look equal.
---

OSPF picks the path whose interface costs add up to the smallest sum, so whatever sets the costs effectively sets the paths. A common default quietly makes all modern links look the same.

### Cost

Each interface has an **OSPF cost**, and a path's cost is the sum along it. Some implementations derive the interface cost from configured bandwidth: faster links get lower costs, until they hit a floor of 1.

```formula reference
C = max(1, ⌊R / B⌋)
where
C: the OSPF cost of the interface: a whole number with no unit; lower means more attractive
R: the reference bandwidth, in megabits per second (Mbit/s); 100 Mbit/s by default in classic Cisco IOS
B: the interface's configured bandwidth, in Mbit/s (1 Gbit/s = 1,000 Mbit/s)
⌊ ⌋: floor: round down to a whole number, since costs are integers
max(1, …): the larger of 1 and the value after it, so the cost never falls below 1
Mbit/s: megabits per second: millions of bits per second
In words: the cost is the reference bandwidth divided by the link's bandwidth, rounded down, but never below 1. Any link at least as fast as the reference therefore gets the minimum cost of 1.
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

## Key takeaways
- OSPF uses configured additive interface costs; the bandwidth formula is an implementation choice.
- The described 100 Mbit/s reference gives every faster interface the minimum cost of one.
- A higher consistent reference distinguishes modern links.
- Compare total path cost, not raw bandwidth or hop count alone.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [Open Shortest Path First — Wikipedia](https://en.wikipedia.org/wiki/Open_Shortest_Path_First)
- [Distance-vector routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)

- [RFC 5838: OSPFv3 address families](https://www.rfc-editor.org/rfc/rfc5838.html)
- [Cisco OSPF FAQ: costs and operational details](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html)
