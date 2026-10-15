---
id: ip-igp-count-to-infinity
title: Trace and limit count to infinity
level: intermediate
minutes: 3
sourceLesson: ip-interior-routing
summary: Follow a failed route through a distance-vector loop and assess the limits of split horizon and poisoning.
---

Follow a failed route through a distance-vector loop and assess the limits of split horizon and poisoning.

### Count to infinity

Distance vector has a famous failure. Take three routers in a line, with network N attached to C. The numbers beneath the routers are their initial hop-count costs to N:

```
 N --- C ------ B ------ A
      1        2        3
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

## Key takeaways
- Stale neighbour information can make routers repeatedly increase a false distance.
- Split horizon suppresses reverse advertisements; poison reverse advertises infinity back.
- Triggered updates and implementation-specific hold-downs change recovery behaviour.
- Two-router fixes do not eliminate all longer loops.

## Further reading
- [RFC 2328: OSPF Version 2](https://www.rfc-editor.org/rfc/rfc2328)
- [RFC 2453: RIP Version 2](https://www.rfc-editor.org/rfc/rfc2453)
- [Open Shortest Path First — Wikipedia](https://en.wikipedia.org/wiki/Open_Shortest_Path_First)
- [Distance-vector routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Distance-vector_routing_protocol)
- [Link-state routing protocol — Wikipedia](https://en.wikipedia.org/wiki/Link-state_routing_protocol)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)

- [RFC 5838: OSPFv3 address families](https://www.rfc-editor.org/rfc/rfc5838.html)
- [Cisco OSPF FAQ: costs and operational details](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html)
