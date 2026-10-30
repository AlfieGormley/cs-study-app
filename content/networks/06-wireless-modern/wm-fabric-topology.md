---
id: wm-fabric-topology
title: From hierarchical trees to leaf-spine fabrics
level: intermediate
minutes: 3
summary: In the fully connected two-tier model, different-leaf traffic traverses leaf, spine, leaf.
sourceLesson: wm-datacentre
---

A service request may fan out to authentication, caches, databases and other services. This can create substantial **east–west** traffic between servers, alongside **north–south** traffic entering or leaving the facility. The actual traffic mix is workload-dependent.

Classic enterprise networks were built for north–south traffic: a hierarchy that funnels traffic between branches of the aggregation layer through a core. A common alternative is a **leaf-spine** fabric, a folded **Clos** topology. Under the simple fully connected model below, each leaf pair has multiple paths of equal configured routing cost, not necessarily identical delay or available bandwidth.

## Why the tree broke

The traditional design had three layers:

```
         [core]     [core]
        /      \   /      \
     [agg]    [agg]     [agg]
     / \       / \       / \
  [acc][acc][acc][acc][acc][acc]
   |    |    |    |    |    |
  servers in racks
```

Problems for east–west traffic:

- **Bottlenecks up the tree.** Traffic between racks in different branches must climb to the core, so aggregate demand can exceed upstream capacity. The required equipment depends on the scale and traffic design.
- **Spanning Tree.** Layer 2 designs ran the Spanning Tree Protocol to prevent loops, which works by *blocking* redundant links. A redundant pair may have only one forwarding path for a particular spanning-tree instance; not every design strands exactly half of all capacity.
- **Uneven latency.** Two servers might be one hop apart or five, depending on where they sit.

## Leaf-spine: a folded Clos network

In 1953 Charles Clos showed how to build large non-blocking telephone switches out of many small ones arranged in stages. Data centres apply the same idea to packet switches:

```
  [S1]   [S2]   [S3]   [S4]   spines
   |\ \  /| |\  /| |\  / /|
   (every leaf to every spine)
   |/ /  \| |/  \| |/  \ \|
  [L1]   [L2]   [L3]   [L4]   leaves
   ||     ||     ||     ||
 servers servers servers servers
```

- In this example each rack has one **leaf** switch; real designs may use dual attachment or other placements.
- Every leaf connects to **every** spine. Spines do not connect to each other, and leaves do not connect to leaves.
- A path between these different leaves traverses three switches: source leaf → spine → destination leaf. Service chains, other fabric tiers and same-leaf traffic differ.
- Between two leaves there are as many equal paths as there are spines. With 4 spines, 4 paths.

> [!analogy] Real-world analogy: Regional airports and hub airports
> Imagine an airline where every regional airport has a direct flight to every hub, hubs never fly to each other, and regional airports never fly to each other. Any trip between two regional airports is exactly two flights: out to a hub and back to the destination. Whichever hub you pick, the trip is the same length, and if one hub closes you simply route through another.
>
> **How it maps:** Regional airports are leaf switches, hubs are spine switches, and every regional-to-hub route is a leaf-to-spine link. The choice of hub is the choice among equal-cost paths, and a closed hub is a failed spine that removes some capacity but strands no airport.
>
> **Where it stops:** Packets are not booked in advance; each switch forwards using hashed path choices and routing tables, and many flows can crowd the same hub at once. Adding a regional airport needs a free gate at every hub, just as a new leaf needs a free port on every spine.

Such fabrics can use fixed-port switches, which need not be identical. Adding spines also needs ports and links on every participating leaf. Adding leaves consumes spine ports; cost and topology limits remain.

Links are normally **layer 3** (routed), not layer 2. Each switch runs a routing protocol; RFC 7938 describes the common choice of eBGP, with an ASN allocation scheme suited to the topology and loop-prevention policy. L3 ECMP can use redundant links without STP blocking, but routing convergence, route limits and failure containment require appropriate design. Where tenants need layer 2 segments, an overlay such as VXLAN carries them over the routed fabric (covered in the SDN lesson).

## Key takeaways
- In the fully connected two-tier model, different-leaf traffic traverses leaf, spine, leaf.
- Routed parallel links remove STP blocking from that fabric; they still need routing and failure design.

## Further reading
- [Clos network — Wikipedia](https://en.wikipedia.org/wiki/Clos_network)
- [RFC 7938: Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938)
